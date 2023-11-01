from functools import wraps
import inspect
from typing import Callable

import typer

from . import config


# def merge(f1: Callable) -> Callable:
    # https://docs.python.org/3/library/functools.html#functools.update_wrapper
    # wraps, but it combines the signatures of the two functions
    # This will allow us to add/remove the `debug` arg depending on config context


def debug_guard(f: Callable) -> Callable:
    if not config.DEBUG:
        return f
    try:
        import snoop  # type: ignore
    except ImportError:
        typer.echo("Debug mode requires the dev group to be installed")
        raise typer.Exit(1)
    else:
        snoop.install(**config.snoop["install"])

    @wraps(f)
    def debug_mode(
        *args,
        **kwargs,
    ) -> Callable:
        typer.echo(f"Debug mode enabled: {inspect.stack()[1].filename}")
        if kwargs.get("debug", False):
            # Snoop depth is set to compensate for wrapper stack frames
            return snoop.snoop(**config.snoop["snoop"])(f)(*args, **kwargs) # noqa: F821 #* ss is installed in debug_mode
        else:
            return f(*args, **kwargs)

    return debug_mode
