from functools import wraps
import inspect
from typing import Callable

import typer

from .config import config


def get_debug_f(f: Callable) -> Callable:
    import snoop  # type: ignore

    return wraps(f)(snoop.snoop(**config.snoop["snoop"])(f))


def debug_guard(f: Callable) -> Callable:
    """A decorator that contextually enables debug mode for the decorated function

    Args:
        f (Callable): The function to decorate

    Raises:
        typer.Exit: Exit CLI if the dev group is not installed

    Returns:
        Callable: The decorated function
    """
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
        debug_f = get_debug_f(f)
        if kwargs.get("debug", False):
            # Snoop depth is set to compensate for wrapper stack frames
            return debug_f(*args, **kwargs)  # noqa: F821 #* ss is installed in debug_mode
        else:
            return f(*args, **kwargs)

    return debug_mode
