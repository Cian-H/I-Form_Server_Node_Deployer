from functools import wraps
from pathlib import Path
from typing import Callable

import config


def ensure_build_dir(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        Path(config.BUILD_DIR).mkdir(exist_ok=True, parents=True)
        return f(*args, **kwargs)

    return wrapper
