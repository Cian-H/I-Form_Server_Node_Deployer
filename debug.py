from functools import wraps
import inspect
from typing import Callable

import typer  # type: ignore

import config


def debug_guard(f: Callable) -> Callable:
    if not config.DEBUG:
        return f
    try:
        import snoop  # type: ignore
    except ImportError:
        typer.echo("Debug mode requires the snoop package")
        raise typer.Exit(1)
    else:
        snoop.install(
            snoop="ss",
        )
    
    typer.echo(f"Debug mode enabled: {inspect.stack()[1].filename}")
    wraps(f)(ss)(f)  # noqa: F821 #* ss is installed in debug_mode
