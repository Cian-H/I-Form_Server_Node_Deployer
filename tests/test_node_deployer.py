import atexit
import filecmp
import os
from pathlib import Path
import pickle
import shutil
from ipaddress import IPv4Address, IPv6Address

from hypothesis import given
from hypothesis import strategies as st
from node_deployer.config import config
import tomllib


config.update_config("test")
config.BUILD_DIR = config.BUILD_DIR / f"tests/{os.getpid()}"


def remove_pid_build_dir():
    shutil.rmtree(config.BUILD_DIR, ignore_errors=True)


def remove_test_build_dir():
    test_build_dir = config.BUILD_DIR.parent
    if any(test_build_dir.iterdir()):
        try:
            test_build_dir.rmdir()
        except OSError:
            pass


def cleanup():
    remove_pid_build_dir()
    remove_test_build_dir()


atexit.register(cleanup)

from node_deployer import ip_interface, autoignition, create_disk, create_img  # noqa: E402


with open(config.PROJECT_ROOT / "tests/data/node_deployer/test_args.toml", "rb") as f:
    TEST_PARAMS = tomllib.load(f)

TEST_DATA_DIR = config.PROJECT_ROOT / "tests/data/node_deployer"


class TestIPInterface:
    TEST_ATTRS = (
        "compressed",
        "exploded",
        "is_global",
        "is_link_local",
        "is_loopback",
        "is_multicast",
        "is_private",
        "is_reserved",
        "is_unspecified",
        "max_prefixlen",
        "packed",
        "reverse_pointer",
        "version",
    )
    
    @given(st.ip_addresses(v=4))
    def test_ipv4_parsing(self, ip: IPv4Address):
        ip_str = str(ip)
        test_result = ip_interface.IPAddress(ip_str)
        assert test_result.obj == ip
    
    @given(st.ip_addresses(v=4))
    def test_ipv4_attr_passthrough(self, ip: IPv4Address):
        # Should be able to access all attributes of ipaddress.IPv4Address directly,
        # not just a copy of the attribute object at instantiation
        ip_addr = ip_interface.IPAddress(str(ip))
        for attr in self.TEST_ATTRS:
            assert getattr(ip_addr, attr) is getattr(ip_addr.obj, attr)
    
    @given(st.ip_addresses(v=4))
    def test_ipv4_bool(self, ip: IPv4Address):
        ip_addr = ip_interface.IPAddress(str(ip))
        assert bool(ip_addr) != ip.is_unspecified
    
    @given(st.ip_addresses(v=6))
    def test_ipv6_parsing(self, ip: IPv6Address):
        ip_str = str(ip)
        test_result = ip_interface.IPAddress(ip_str)
        assert test_result.obj == ip
    
    @given(st.ip_addresses(v=6))
    def test_ipv6_attr_passthrough(self, ip: IPv6Address):
        # Should be able to access all attributes of ipaddress.IPv4Address directly,
        # not just a copy of the attribute object at instantiation
        ip_addr = ip_interface.IPAddress(str(ip))
        for attr in self.TEST_ATTRS:
            assert getattr(ip_addr, attr) is getattr(ip_addr.obj, attr)
    
    @given(st.ip_addresses(v=6))
    def test_ipv6_bool(self, ip: IPv6Address):
        ip_addr = ip_interface.IPAddress(str(ip))
        assert bool(ip_addr) != ip.is_unspecified


class TestAutoignition:
    def test_json_to_img(self, tmp_path: Path):
        tmp_path.mkdir(parents=True, exist_ok=True)
        autoignition.json_to_img(
            TEST_DATA_DIR / "fuelignition.json",
            tmp_path / "ignition.img",
        )
        assert filecmp.cmp(
            TEST_DATA_DIR / "ignition.img",
            tmp_path / "ignition.img",
        )


class TestCreateImg:
    def test_load_template(self):
        template = create_img.load_template()
        with open(TEST_DATA_DIR / "create_img/load_template.pkl", "rb") as f:
            assert pickle.load(f) == template

    def test_apply_ignition_settings(self):
        with open(
            TEST_DATA_DIR / "create_img/load_template.pkl",
            mode="rb",
        ) as f:
            template = pickle.load(f)
        test_result = create_img.apply_ignition_settings(
            template,
            **TEST_PARAMS["create_img"]["apply_ignition_settings"],
        )
        with open(
            TEST_DATA_DIR / "create_img/apply_ignition_settings.pkl",
            mode="rb",
        ) as f:
            expected = pickle.load(f)

        assert expected == test_result

    def test_create_img(self, tmp_path: Path):
        tmp_path.mkdir(parents=True, exist_ok=True)
        create_img.create_img(
            **TEST_PARAMS["create_img"]["create_img"],
            img_path=tmp_path / "ignition.img",
        )
        assert filecmp.cmp(
            tmp_path / "ignition.img",
            TEST_DATA_DIR / "ignition.img",
        )


class TestCreateDisk:
    def init_buildfile(self, filename: str):
        config.BUILD_DIR.mkdir(parents=True, exist_ok=True)
        test_target = config.BUILD_DIR / filename
        if not test_target.exists():
            test_target.write_bytes(Path(TEST_DATA_DIR / filename).read_bytes())

    def test_filter_validation_response(self):
        self.init_buildfile("config.ign")
        with open(TEST_DATA_DIR / "create_disk/validation_result.pkl", "rb") as f:
            input = pickle.load(f)
        test_result = create_disk.filter_validation_response(input)
        assert test_result == ""

    def test_validation_result(self):
        self.init_buildfile("config.ign")
        test_result = create_disk.validation_result()
        with open(TEST_DATA_DIR / "create_disk/validation_result.pkl", "rb") as f:
            expected = pickle.load(f)
        assert test_result == expected

    def test_validate(self):
        self.init_buildfile("config.ign")
        test_result = create_disk.validate()
        assert test_result == (True, "")
