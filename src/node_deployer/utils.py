from functools import wraps
from pathlib import Path
from typing import Callable
import docker

from .config import config


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


def next_free_tcp_port(port: int) -> int:
    """Finds the next free port after the specified port

    Args:
        port (int): The port to start searching from
        
    Raises:
        ValueError: If no free ports are found

    Returns:
        int: The next free port
    """
    ports = []
    try:
        containers = config.CLIENT.containers.list(all=True)
        ports = []
        for container in containers:
            port_values = container.ports.values()
            if not port_values:
                continue
            for x in list(container.ports.values())[0]:
                ports.append(int(x["HostPort"]))
    except docker.errors.NotFound:  # type: ignore
        #* This error is raised if container list changes between getting the list and
        #* getting the ports. If this happens, just try again
        return next_free_tcp_port(port)
    if not ports:
        return port
    ports = set(ports)
    while port in ports:
        port += 1
        if port > 65535:
            raise ValueError("No free ports")
    return port
    