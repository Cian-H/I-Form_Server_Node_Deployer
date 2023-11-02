import filecmp
import pickle

from node_deployer import create_img
from node_deployer.config import config


class TestCreateImg:
    def test_load_template(self):
        template = create_img.load_template()
        with open(
            config.PROJECT_ROOT / "tests/test_node_deployer/data/create_img/load_template.pkl", "rb"
        ) as f:
            assert pickle.load(f) == template

    def test_apply_ignition_settings(self):
        with open(
            config.PROJECT_ROOT / "tests/test_node_deployer/data/create_img/load_template.pkl",
            mode="rb",
        ) as f:
            template = pickle.load(f)
        test_result = create_img.apply_ignition_settings(
            template,
            "test_hostname",
            "",
            {
                "SWITCH_IP_ADDRESS": "192.168.1.1",
                "SWITCH_PORT": 42,
                "SWARM_TOKEN": "SWMTKN-1-THISISATESTSWARMTOKENFORTESTINGPURPOSESANDTHATMEANSITNEEDSTOBEQUITELONG",  # noqa: E501
            },
        )
        with open(
            config.PROJECT_ROOT
            / "tests/test_node_deployer/data/create_img/apply_ignition_settings.pkl",
            mode="rb",
        ) as f:
            assert pickle.load(f) == test_result

    def test_create_img(self, tmpdir):
        create_img.create_img(
            hostname="test_hostname",
            password="",
            switch_ip="192.168.1.1",
            switch_port=42,
            img_path=tmpdir / "ignition.img",
        )
        assert filecmp.cmp(
            tmpdir / "ignition.img",
            config.PROJECT_ROOT / "tests/test_node_deployer/data/ignition.img",
        )
