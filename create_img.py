import ipaddress
import json
from typing import Annotated

import typer

from autoignition import json_to_img
from cli import cli_spinner
import config
from debug import debug_guard
from utils import ensure_build_dir


MAX_PORT: int = 65535


def load_template() -> dict:
    with open("templates/fuelignition.json", "r") as f:
        out = json.load(f)
    return out


def apply_ignition_settings(
    template: dict,
    hostname: str,
    password: str,
    swarm_config: str,
) -> dict:
    ignition_config = template.copy()
    ignition_config["hostname"] = hostname
    ignition_config["login"]["users"][0]["passwd"] = password

    # Add files that will define a service to ensure that the node joins the swarm
    with open("templates/join_swarm.sh", "r") as f1, open(
        "templates/join_swarm.service", "r"
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
    switch_ip_address = ipaddress.ip_address(switch_ip_address)
    if switch_port > MAX_PORT:
        raise ValueError(f"Port must be less than {MAX_PORT}")

    # get swarm configuration as JSON
    swarm_config = json.dumps(
        {
            "SWITCH_IP_ADDRESS": str(switch_ip_address),
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
    with open("build/fuelignition.json", "w") as f:
        json.dump(ignition_config, f, indent=4)

    # convert ignition configuration to image
    json_to_img("build/fuelignition.json", "build/ignition.img")


if __name__ == "__main__":
    config.update_config("cli")
    typer.run(create_img)
