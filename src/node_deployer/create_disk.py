from fnmatch import fnmatch
import ipaddress
from typing import Annotated

from docker.types import Mount
import typer

from . import config
from .cli import cli_spinner
from .create_img import create_img
from .debug import debug_guard
from .utils import ensure_build_dir


type IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address


def filter_validation_response(response: str) -> str:
    return "\n".join(
        filter(
            # Filter out the warning about unused key human_readable, this always exists in
            # configurations produced by fuel-ignition
            lambda x: not fnmatch(x.strip(), "warning at*Unused key human_read"),
            response.split("\n"),
        )
    ).strip()


def validation_result() -> str:
    dockerfile = config.DOCKERFILE_DIR / "validate.dockerfile"
    image, _ = config.CLIENT.images.build(
        path=".",
        dockerfile=str(dockerfile),
        tag="validate",
        buildargs={"CWD_MOUNTDIR": str(config.CWD_MOUNTDIR)},
        rm=config.CLEANUP_IMAGES,
        pull=True,
        quiet=True,
    )
    response = config.CLIENT.containers.run(
        image,
        mounts=[
            config.CWD_MOUNT,
        ],
        remove=True,
    )
    if config.CLEANUP_IMAGES:
        image.remove(force=True)
    return response


@cli_spinner(description="Validating ignition image", total=None)
def validate() -> (bool, str):
    response = validation_result().decode()
    response = filter_validation_response(response)
    return (not bool(response), response)


@cli_spinner(description="Writing ignition image to disk", total=None)
def write_disk(disk: str) -> None:
    config.CLIENT.containers.run(
        "alpine",
        mounts=[config.CWD_MOUNT, Mount("/ignition_disk", disk, type="bind")],
        privileged=True,
        command=f"dd if={config.CWD_MOUNTDIR}/build/ignition.img of=/ignition_disk",
    )


@debug_guard
@cli_spinner(description="Creating ignition initialisation disk", total=None)
@ensure_build_dir
def create_ignition_disk(
    disk: Annotated[
        str,
        typer.Option(
            "--disk",
            "-d",
            help="Path to the disk to write to",
            prompt=True,
        ),
    ] = None,
    hostname: Annotated[
        str,
        typer.Option(
            "--hostname",
            "-h",
            help="Hostname for the new node",
            prompt=True,
        ),
    ] = "node",
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-p",
            help="Password for the root user on the new node",
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
        ),
    ] = None,
    switch_ip: Annotated[
        IPAddress,
        typer.Option(
            "--switch-ip",
            "-ip",
            help="IP address of the switch to connect to",
            prompt=True,
            parser=ipaddress.ip_address,
        ),
    ] = None,
    switch_port: Annotated[
        int,
        typer.Option(
            "--switch-port",
            "-sp",
            help="Port on the switch to connect to",
            prompt=True,
            min=1,
            max=config.MAX_PORT,
        ),
    ] = 4789,
    swarm_token: Annotated[
        str,
        typer.Option(
            "--swarm-token",
            "-t",
            help="Swarm token for connecting to the swarm",
            prompt=True,
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug mode",
            is_eager=True,
            is_flag=True,
            flag_value=True,
            hidden=not config.DEBUG,
        )
    ] = False,
) -> None:
    """Writes an ignition image to the specified disk for easy deployment of new nodes to the swarm"""  # noqa
    create_img(
        hostname = hostname,
        password = password,
        switch_ip = switch_ip,
        switch_port = switch_port,
        swarm_token = swarm_token,
        img_path = config.BUILD_DIR / "ignition.img",
        debug = debug,
    )
    valid, response = validate()
    if not valid:
        print(response)
        raise typer.Exit(1)
    else:
        print("Valid ignition image created!")
    write_disk(disk)


if __name__ == "__main__":
    config.update_config("cli")
    typer.run(create_ignition_disk)
