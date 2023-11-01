import typer

from . import config
from .autoignition import json_to_img
from .create_disk import create_ignition_disk
from .create_img import create_img


cmd_params = {
    "no_args_is_help": True,
}

app = typer.Typer(
    help="A tool for creating ignition images for automated deployment to a swarm",
    **cmd_params,
)

app.command(**cmd_params)(create_img)
app.command(**cmd_params)(create_ignition_disk)
app.command(**cmd_params)(json_to_img)

if __name__ == "__main__":
    config.update_config("cli")
    app()