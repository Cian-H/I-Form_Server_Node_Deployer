from fnmatch import fnmatch
from typing import Annotated

import typer

import config
from create_img import create_img
from debug import debug_guard
from utils import ensure_build_dir
from docker.types import Mount


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


def validate() -> (bool, str):
    response = validation_result().decode()
    response = filter_validation_response(response)
    return (not bool(response), response)


def write_disk(disk: str) -> None:
    config.CLIENT.containers.run(
        "alpine",
        mounts=[config.CWD_MOUNT, Mount("/ignition_disk", disk, type="bind")],
        privileged=True,
        command=f"dd if={config.CWD_MOUNTDIR}/build/ignition.img of=/ignition_disk",
    )


@debug_guard
@ensure_build_dir
def create_ignition_disk(
    disk: Annotated[str, typer.Option(help="Path to the disk to write to", prompt=True)],
    hostname: Annotated[str, typer.Option(help="Hostname for the new node", prompt=True)],
    password: Annotated[
        str,
        typer.Option(
            help="Password for the root user on the new node",
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
        ),
    ],
    switch_ip_address: Annotated[
        str, typer.Option(help="IP address of the switch to connect to", prompt=True)
    ],
    switch_port: Annotated[int, typer.Option(help="Port on the switch to connect to", prompt=True)],
    swarm_token: Annotated[
        str, typer.Option(help="Swarm token for connecting to the swarm", prompt=True)
    ],
) -> None:
    create_img(hostname, password, switch_ip_address, switch_port, swarm_token)
    valid, response = validate()
    if not valid:
        print(response)
        raise typer.Exit(1)
    else:
        print("Valid ignition image created!")
    write_disk(disk)


if __name__ == "__main__":
    typer.run(create_ignition_disk)
