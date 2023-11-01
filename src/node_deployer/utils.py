from functools import wraps
from pathlib import Path
from typing import Callable

from . import config


def ensure_build_dir(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        Path(config.BUILD_DIR).mkdir(exist_ok=True, parents=True)
        return f(*args, **kwargs)

    return wrapper


class Singleton(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
