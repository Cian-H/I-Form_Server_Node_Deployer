from functools import wraps
from pathlib import Path
from typing import Callable

from . import config


def ensure_build_dir(f: Callable) -> Callable:
    """Ensures that the build directory exists before running the decorated function

    Args:
        f (Callable): The function to decorate

    Returns:
        Callable: The decorated function
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        Path(config.BUILD_DIR).mkdir(exist_ok=True, parents=True)
        return f(*args, **kwargs)

    return wrapper


class Singleton(type):
    """A singleton metaclass"""
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        """Creates a new instance of the class if one does not already exist

        Returns:
            cls._instance: The instance of the class
        """
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
