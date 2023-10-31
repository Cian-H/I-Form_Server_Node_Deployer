#!/usr/bin/env poetry run python

from autoignition import json_to_img
import config
from create_disk import create_ignition_disk
from create_img import create_img
import typer


app = typer.Typer(
    help="A tool for creating ignition images for automated deployment to a swarm"
)

app.command()(create_img)
app.command()(create_ignition_disk)
app.command()(json_to_img)

if __name__ == "__main__":
    config.update_config("cli")
    app()