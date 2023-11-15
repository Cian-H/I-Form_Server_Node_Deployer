import flet as ft
import typer
from typing import Dict, Any

from node_deployer.config import config
from node_deployer import app as _cli_app
from node_deployer_gui import main as gui_main


cmd_params: Dict[Any, Any] = config.typer

app = typer.Typer(
    help="A tool for creating ignition images for automated deployment to a swarm",
    **{key: value for key, value in cmd_params.items() if key != "no_args_is_help"},
)


@app.command(name="gui", help="The GUI interface for the node deployer", **cmd_params)
@app.callback(invoke_without_command=True)
def gui_app():
    ft.app(target=gui_main)


@app.command(name="cli", help="The CLI interface for the node deployer", **cmd_params)
def cli_app():
    config.update_config("cli")
    _cli_app()


if __name__ == "__main__":
    app()
