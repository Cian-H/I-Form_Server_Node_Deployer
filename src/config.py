# flake8: noqa: F821
#* This file sets a number of config constants by modifying its own globals
#* As a result, F821 is disabled as the intereter cannot be trusted to know
#* when F821 should be raised.

from pathlib import Path

import docker
import tomllib


CLIENT = docker.from_env(version="auto")
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

type ConfigLabel = str | list[str]


def get_config(config_label: ConfigLabel = ["default"]) -> dict:
    if isinstance(config_label, str):
        config_label = [config_label]
    with open(PROJECT_ROOT / "config.toml", "rb") as f:
        configs: dict = tomllib.load(f)
    out_config: dict = {}
    for c in config_label:
        out_config.update(configs[c])
    return out_config


def finalise_config(config: dict) -> None:
    # First, convert base paths to Path objects
    for k, v in config.items():
        match k:
            case "SRC_DIR" | "BUILD_DIR":
                config[k] = Path(v).absolute()
            case "CWD_MOUNTDIR":
                config[k] = Path(v)
    # Then, get required paths from config or globals if not present
    build_dir = config.get("BUILD_DIR", BUILD_DIR)
    cwd_mountdir = config.get("CWD_MOUNTDIR", CWD_MOUNTDIR)
    src_dir = config.get("SRC_DIR", SRC_DIR)
    # Finally, construct the secondary parameters
    config["FUELIGNITION_BUILD_DIR"] = build_dir / config.get(
        "FUELIGNITION_BUILD_DIR",
        FUELIGNITION_BUILD_DIR
    )
    config["DOCKERFILE_DIR"] = src_dir / config.get(
        "DOCKERFILE_DIR",
        DOCKERFILE_DIR
    )
    config["CWD_MOUNT"] = docker.types.Mount(
        target=str(cwd_mountdir),
        source=str(PROJECT_ROOT),
        type="bind",
    )


def apply_config(config: dict) -> None:
    finalise_config(config)
    globals().update(config)
    

def update_config(config_label: ConfigLabel = "default") -> None:
    apply_config(get_config(config_label))


def init() -> None:
    globals().update(get_config())
    update_config()

init()