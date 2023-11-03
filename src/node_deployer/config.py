from pathlib import Path
from types import SimpleNamespace
from typing import Union

import docker
import tomllib


CLIENT = docker.from_env(version="auto")
MAX_PORT: int = 65535


def __get_project_root():
    r = Path(__file__)
    while r.name != "src":
        r = r.parent
    return r.parent


PROJECT_ROOT: Path = __get_project_root()

ConfigLabel = Union[str, list[str]]  # After PEP695 support: type ConfigLabel = str | list[str]


class Config(SimpleNamespace):
    def __init__(self, config_label: ConfigLabel, **kwargs) -> None:
        """Initialises the configuration object

        Args:
            config_label (ConfigLabel): The configuration to initialise with
            **kwargs: Additional keyword arguments to become attributes
        """
        self.__dict__.update(self.get_config(config_label))
        self.update_config()
        _kwargs = {
            "CLIENT": CLIENT,
            "MAX_PORT": MAX_PORT,
            "PROJECT_ROOT": PROJECT_ROOT,
        }
        _kwargs.update(kwargs)
        super().__init__(**_kwargs)

    @staticmethod
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

    def finalise_config(self, config: dict) -> None:
        """Finalises the configuration by converting paths to Path objects and
        appropriately setting secondary parameters such as relative paths

        Args:
            config (dict): The configuration to finalise
        """
        # First, convert base paths to Path objects
        for k, v in config.items():
            match k:
                case "SRC_DIR" | "BUILD_DIR":
                    config[k] = Path(PROJECT_ROOT / v).absolute()
                case "CWD_MOUNTDIR":
                    config[k] = Path(v)
        # Then, get required paths from config or globals if not present
        build_dir = Path(config.get("BUILD_DIR", self.BUILD_DIR)).absolute()
        cwd_mountdir = Path(config.get("CWD_MOUNTDIR", self.CWD_MOUNTDIR))
        src_dir = Path(config.get("SRC_DIR", self.SRC_DIR)).absolute()
        # Finally, construct the secondary parameters
        config["FUELIGNITION_BUILD_DIR"] = build_dir / config.get(
            "FUELIGNITION_BUILD_DIR", self.FUELIGNITION_BUILD_DIR
        )
        config["DOCKERFILE_DIR"] = src_dir / config.get("DOCKERFILE_DIR", self.DOCKERFILE_DIR)
        # I really wish docker-py had typeshed stubs
        config["CWD_MOUNT"] = docker.types.Mount(  # type: ignore
            target=str(cwd_mountdir),
            source=str(PROJECT_ROOT),
            type="bind",
        )

    def apply_config(self, config: dict) -> None:
        """Applies the specified configuration to this object's attributes

        Args:
            config (dict): The configuration to apply
        """
        self.finalise_config(config)
        self.__dict__.update(config)

    def update_config(self, config_label: ConfigLabel = "default") -> None:
        """Updates the configuration to the specified configuration

        Args:
            config_label (ConfigLabel, optional):
                The label of the configuration to update to.
                Defaults to "default".
        """
        self.apply_config(self.get_config(config_label))


config = Config(config_label="default")
