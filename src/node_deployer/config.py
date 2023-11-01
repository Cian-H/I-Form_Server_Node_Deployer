# flake8: noqa: F821
# type: ignore
#* This file sets a number of config constants by modifying its own globals
#* As a result, F821 and typing is disabled as the interpreter cannot be
#* trusted to know when F821 or UndefinedVeriable errors should be raised.

from pathlib import Path

import docker
import tomllib


CLIENT = docker.from_env(version="auto")
MAX_PORT: int = 65535
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.absolute()

type ConfigLabel = str | list[str]


def get_config(config_label: ConfigLabel = "default") -> dict:
    """Gets the specified configuration from config.toml

    Args:
        config_label (ConfigLabel, optional):
            The label of the configuration to get.
            Defaults to "default".

    Returns:
        dict: The specified configuration
    """
    if isinstance(config_label, str):
        config_label = [config_label]
    with open(PROJECT_ROOT / "config.toml", "rb") as f:
        configs: dict = tomllib.load(f)
    out_config: dict = {}
    for c in config_label:
        out_config.update(configs[c])
    return out_config


def finalise_config(config: dict) -> None:
    """Finalises the configuration by converting paths to Path objects and
    appropriately setting secondary parameters such as relative paths

    Args:
        config (dict): The configuration to finalise
    """
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
    """Applies the specified configuration to this module's globals

    Args:
        config (dict): The configuration to apply
    """
    finalise_config(config)
    globals().update(config)
    

def update_config(config_label: ConfigLabel = "default") -> None:
    """Updates the configuration to the specified configuration

    Args:
        config_label (ConfigLabel, optional):
            The label of the configuration to update to.
            Defaults to "default".
    """
    apply_config(get_config(config_label))


def init(config_label: ConfigLabel) -> None:
    """Initialises the configuration module

    Args:
        config_label (ConfigLabel): The configuration to initialise with
    """
    globals().update(get_config(config_label))
    update_config()


init(config_label="default")