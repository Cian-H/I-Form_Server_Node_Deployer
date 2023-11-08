from fnmatch import fnmatch
from typing import Annotated, Optional

from docker.types import Mount
import typer

from .cli import cli_spinner
from .config import config
from .create_img import create_img
from .debug import debug_guard
from .ip_interface import IPAddress
from .utils import ensure_build_dir


def filter_validation_response(response: str) -> str:
    """Filters out erroneous warnings from the validation response

    Args:
        response (str): The response to filter

    Returns:
        str: The filtered response
    """
    return "\n".join(
        filter(
            # Filter out the warning about unused key human_readable, this always exists in
            # configurations produced by fuel-ignition
            lambda x: not fnmatch(x.strip(), "warning at*Unused key human_read"),
            response.split("\n"),
        )
    ).strip()


def validation_result() -> str:
    """Returns the response resulting from a validation of the ignition image

    Returns:
        str: The response from the validation
    """
    dockerfile = config.DOCKERFILE_DIR / "validate.dockerfile"
    image, _ = config.CLIENT.images.build(
        path=".",
        dockerfile=str(dockerfile),
        tag="validate",
        buildargs={
            "CWD_MOUNTDIR": str(config.CWD_MOUNTDIR),
            "BUILD_DIR": str(config.BUILD_DIR.relative_to(config.PROJECT_ROOT)),
        },
        rm=config.CLEANUP_IMAGES,
        pull=True,
        quiet=True,
    )
    response = config.CLIENT.containers.run(
        image,
        mounts=[
            config.CWD_MOUNT,
        ],
        remove=config.CLEANUP_IMAGES,
    )
    if config.CLEANUP_IMAGES:
        image.remove(force=True)
    return response.decode()


@cli_spinner(description="Validating ignition image", total=None)
def validate() -> tuple[bool, str]:
    """Validates the ignition image

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating whether
        the validation was successful and the response from the validation
    """
    response = validation_result()
    response = filter_validation_response(response)
    return (not bool(response), response)


@cli_spinner(description="Writing ignition image to disk", total=None)
def write_disk(disk: str) -> None:
    """Writes the ignition image to the specified disk

    Args:
        disk (str): The disk to write to
    """
    config.CLIENT.containers.run(
        "alpine",
        mounts=[config.CWD_MOUNT, Mount("/ignition_disk", disk, type="bind")],
        privileged=True,
        command=f"dd if={config.CWD_MOUNTDIR}/build/ignition.img of=/ignition_disk",
        remove=config.CLEANUP_CONTAINERS,
    )


@debug_guard
@cli_spinner(description="Creating ignition initialisation disk", total=None)
@ensure_build_dir
def create_ignition_disk(
    disk: Annotated[
        Optional[str],
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
        Optional[str],
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
        Optional[IPAddress],
        typer.Option(
            "--switch-ip",
            "-ip",
            help="IP address of the switch to connect to",
            prompt=True,
            parser=IPAddress,
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
        Optional[str],
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
        ),
    ] = False,
) -> None:
    """Creates an ignition image and writes it to the specified disk

    Args:
        disk (Annotated[ str, typer.Option, optional):
            The disk to write to.
            Defaults to None.
        hostname (Annotated[ str, typer.Option, optional):
            The hostname for the new node.
            Defaults to "node".
        password (Annotated[ str, typer.Option, optional):
            The password for the root user on the new node.
            Defaults to None.
        switch_ip (Annotated[ IPAddress, typer.Option, optional):
            The IP address of the switch to connect to.
            Defaults to None.
        switch_port (Annotated[ int, typer.Option, optional):
            The port on the switch to connect to.
            Defaults to 4789.
        swarm_token (Annotated[ str, typer.Option, optional):
            The swarm token for connecting to the swarm.
            Defaults to None.
        debug (Annotated[ bool, typer.Option, optional):
            Enable debug mode.
            Defaults to False.

    Raises:
        typer.Exit: Exit CLI if the ignition image is invalid
    """
    # Guard against the user specifying no disk
    if disk is None:
        raise typer.BadParameter("No disk specified")

    create_img(
        hostname=hostname,
        password=password,
        switch_ip=switch_ip,
        switch_port=switch_port,
        swarm_token=swarm_token,
        img_path=config.BUILD_DIR / "ignition.img",
        debug=debug,
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
