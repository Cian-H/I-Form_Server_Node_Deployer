from pathlib import Path

import tomllib

import docker


def get_config(config: str = "default") -> dict:
    with open("config.toml", "rb") as f:
        configs: dict = tomllib.load(f)
    out_config: dict = configs["default"]
    out_config.update(configs[config])
    return out_config


def apply_config(config: dict) -> None:
    config["CLIENT"] = docker.from_env(version="auto")
    config["ROOT_DIR"] = Path(config["ROOT_DIR"]).absolute()
    config["BUILD_DIR"] = Path(config["BUILD_DIR"]).absolute()
    config["DOCKERFILE_DIR"] = Path(config["DOCKERFILE_DIR"]).absolute()
    config["FUELIGNITION_BUILD_DIR"] = config["BUILD_DIR"] / config["FUELIGNITION_BUILD_DIR"]
    config["CWD_MOUNTDIR"] = Path(config["CWD_MOUNTDIR"])
    config["CWD_MOUNT"] = docker.types.Mount(
        target=str(config["CWD_MOUNTDIR"]),
        source=str(config["ROOT_DIR"]),
        type="bind",
    )
    globals().update(config)
    

def init(config: str = "default") -> None:
    apply_config(get_config(config))

init()