from functools import wraps
import inspect
from typing import Callable

from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import config
from .utils import Singleton


class SingletonProgress(Progress, metaclass=Singleton):
    """A singleton progress bar"""
    pass


def cli_spinner(*spinner_args, **spinner_kwargs) -> Callable:
    """A decorator that adds a spinner to the CLI while the decorated function is running
    
    Args:
        *spinner_args: The arguments to pass to the rich spinner object
        **spinner_kwargs: The keyword arguments to pass to the rich spinner object

    Returns:
        Callable: The decorated function
    """
    def decorator(f: Callable) -> Callable:
        # Indent the spinner to match its nesting level
        indent = len(inspect.stack()) - 1
        spinner_kwargs["indent"] = f"├{"─"*indent}► "
        
        @wraps(f)
        def wrapped(*func_args, **func_kwargs):
            if not config.CLI:
                return f(*func_args, **func_kwargs)
            with SingletonProgress(
                SpinnerColumn(),
                TextColumn("{task.fields[indent]}[progress.description]{task.description}"),
                transient=True,
                expand=True,
            ) as progress:
                task_id = progress.add_task(*spinner_args, **spinner_kwargs)
                out = f(*func_args, **func_kwargs)
                progress.stop_task(task_id)
                return out
        return wrapped
    return decorator
