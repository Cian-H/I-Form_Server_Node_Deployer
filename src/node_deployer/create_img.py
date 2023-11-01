import ipaddress
import json
from pathlib import Path
from typing import Annotated

import typer

from . import config
from .autoignition import json_to_img
from .cli import cli_spinner
from .debug import debug_guard
from .utils import ensure_build_dir


type IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address


def load_template() -> dict:
    """Loads the default template for the ignition configuration

    Returns:
        dict: The default ignition configuration
    """
    with open(config.SRC_DIR / "templates/fuelignition.json", "r") as f:
        out = json.load(f)
    return out


def apply_ignition_settings(
    template: dict,
    hostname: str,
    password: str,
    swarm_config: str,
) -> dict:
    """Applies the specified ignition settings to the template

    Args:
        template (dict): The template to apply the settings to
        hostname (str): The hostname to set
        password (str): The password to set for the root user
        swarm_config (str): The swarm configuration to set

    Returns:
        dict: The template with the settings applied
    """
    ignition_config = template.copy()
    ignition_config["hostname"] = hostname
    ignition_config["login"]["users"][0]["passwd"] = password

    # Add files that will define a service to ensure that the node joins the swarm
    with open(config.SRC_DIR / "templates/join_swarm.sh", "r") as f1, open(
        config.SRC_DIR / "templates/join_swarm.service", "r"
    ) as f2:
        swarm_script, swarm_service = f1.read(), f2.read()

    ignition_config["storage"] = ignition_config.get("storage", {})
    ignition_config["storage"]["files"] = ignition_config["storage"].get("files", [])
    ignition_config["storage"]["files"] += [
        {
            "path": "/root/join_swarm.json",
            "source_type": "data",
            "mode": 420,
            "overwrite": True,
            "data_content": swarm_config,
        },
        {
            "path": "/root/join_swarm.sh",
            "source_type": "data",
            "mode": 420,
            "overwrite": True,
            "data_content": swarm_script,
        },
    ]

    ignition_config["systemd"] = ignition_config.get("systemd", {})
    ignition_config["systemd"]["units"] = ignition_config["systemd"].get("units", [])
    ignition_config["systemd"]["units"] += [
        {
            "name": "join_swarm.service",
            "enabled": True,
            "contents": swarm_service,
        },
    ]

    return ignition_config


@debug_guard
@cli_spinner(description="Creating ignition image", total=None)
@ensure_build_dir
def create_img(
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
    img_path: Annotated[
        Path,
        typer.Option(
            "--img-path",
            "-o",
            help="Path to which the ignition image should be written",
            dir_okay=False,
        ),
    ] = Path("ignition.img"),
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
    """Creates an ignition image for a node that will automatically join a swarm

    Args:
        hostname (Annotated[ str, typer.Option, optional):
            The hostname to set for the node.
            Defaults to "node".
        password (Annotated[ str, typer.Option, optional):
            The password to set for the root user on the node.
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
        img_path (Annotated[ Path, typer.Option, optional):
            The path to which the ignition image should be written.
            Defaults to Path("ignition.img").
        debug (Annotated[ bool, typer.Option, optional):
            Enable debug mode.
            Defaults to False.
    """
    # get swarm configuration as JSON
    swarm_config = json.dumps(
        {
            "SWITCH_IP_ADDRESS": str(switch_ip),
            "SWITCH_PORT": switch_port,
            "SWARM_TOKEN": swarm_token,
        }
    )

    # Create ignition configuration
    ignition_config = load_template()
    ignition_config = apply_ignition_settings(
        ignition_config,
        hostname,
        password,
        swarm_config,
    )

    # export ignition configuration
    with open(config.BUILD_DIR / "fuelignition.json", "w") as f:
        json.dump(ignition_config, f, indent=4)

    # convert ignition configuration to image
    json_to_img(
        json_path=config.BUILD_DIR / "fuelignition.json",
        img_path=img_path,
        debug=debug,
    )


if __name__ == "__main__":
    config.update_config("cli")
    typer.run(create_img)
