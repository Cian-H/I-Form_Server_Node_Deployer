from node_deployer.config import config


config.update_config("test")
config.BUILD_DIR = config.BUILD_DIR / "tests"
