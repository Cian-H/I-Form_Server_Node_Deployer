from fnmatch import fnmatch
from pathlib import Path
from typing import Annotated

import typer

from config import (
    CLEANUP_IMAGES,
    CLIENT,
    CWD_MOUNT,
    CWD_MOUNTDIR,
    DOCKERFILE_DIR,
)
from create_img import create_img
from debug import debug_mode
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
    dockerfile = DOCKERFILE_DIR / "validate.dockerfile"
    image, _ = CLIENT.images.build(
        path=".",
        dockerfile=str(dockerfile),
        tag="validate",
        buildargs={"CWD_MOUNTDIR": str(CWD_MOUNTDIR)},
        rm=CLEANUP_IMAGES,
        pull=True,
        quiet=True,
    )
    response = CLIENT.containers.run(
        image,
        mounts=[CWD_MOUNT,],
        remove=True,
    )
    if CLEANUP_IMAGES:
        image.remove(force=True)
    return response


def validate() -> (bool, str):
    response = validation_result().decode()
    response = filter_validation_response(response)
    return (not bool(response), response)


def write_disk(disk: str) -> None:
    CLIENT.containers.run(
        "alpine",
        mounts=[CWD_MOUNT, Mount("/ignition_disk", disk, type="bind")],
        privileged=True,
        command=f"dd if={CWD_MOUNTDIR}/build/ignition.img of=/ignition_disk"
    )


def create_ignition_disk(
    disk: str,
    hostname: str,
    password:  str,
    switch_ip_address: str,
    switch_port: int,
    swarm_token: str,
    debug: bool = False,
) -> None:
    create_img(hostname, password, switch_ip_address, switch_port, swarm_token)
    valid, response = validate()
    if not valid:
        print(response)
        raise typer.Exit(1)
    else:
        print("Valid ignition image created!")
    write_disk(disk)


def main(
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
    debug: Annotated[bool, typer.Option(help="Enable debug mode")] = False,
) -> None:
    debug_mode(debug)
    Path("build").mkdir(exist_ok=True, parents=True)
    f = create_ignition_disk
    if debug:
        f = ss(f)  # noqa: F821, # type: ignore #? ss is installed in debug_mode
    f(disk, hostname, password, switch_ip_address, switch_port, swarm_token)


if __name__ == "__main__":
    typer.run(main)
