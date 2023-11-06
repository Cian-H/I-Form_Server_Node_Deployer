#!/usr/bin/env python

from typing import Any, Dict

import typer

from .autoignition import json_to_img
from .config import config
from .create_disk import create_ignition_disk
from .create_img import create_img


cmd_params: Dict[Any, Any] = config.typer

app = typer.Typer(
    help="A tool for creating ignition images for automated deployment to a swarm",
    **cmd_params,
)

# Register commands
app.command(help=str(create_ignition_disk.__doc__).split("Args:")[0].strip(), **cmd_params)(
    create_ignition_disk
)
app.command(help=str(create_img.__doc__).split("Args:")[0].strip(), **cmd_params)(create_img)
app.command(help=str(json_to_img.__doc__).split("Args:")[0].strip(), **cmd_params)(json_to_img)

if __name__ == "__main__":
    config.update_config("cli")
    app()
