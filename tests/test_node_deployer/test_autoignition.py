import filecmp

from node_deployer import autoignition
from node_deployer.config import config


class TestAutoignition:
    def test_json_to_img(self, tmpdir):
        autoignition.json_to_img(
            config.PROJECT_ROOT / "tests/test_node_deployer/data/fuelignition.json",
            tmpdir / "ignition.img",
        )
        assert filecmp.cmp(
            config.PROJECT_ROOT / "tests/test_node_deployer/data/ignition.img",
            tmpdir / "ignition.img",
        )
