import atexit
import filecmp
from pathlib import Path
import pickle
import shutil

from node_deployer.config import config
import tomllib


config.update_config("test")
config.BUILD_DIR = config.BUILD_DIR / "tests"
atexit.register(lambda: shutil.rmtree(config.BUILD_DIR, ignore_errors=True))

from node_deployer import autoignition, create_img  # noqa: E402


with open(config.PROJECT_ROOT / "tests/data/node_deployer/test_args.toml", "rb") as f:
    TEST_PARAMS = tomllib.load(f)


class TestAutoignition:
    def test_json_to_img(self, tmp_path: Path):
        tmp_path.mkdir(parents=True, exist_ok=True)
        autoignition.json_to_img(
            config.PROJECT_ROOT / "tests/data/node_deployer/fuelignition.json",
            tmp_path / "ignition.img",
        )
        assert filecmp.cmp(
            config.PROJECT_ROOT / "tests/data/node_deployer/ignition.img",
            tmp_path / "ignition.img",
        )


class TestCreateImg:
    def test_load_template(self):
        template = create_img.load_template()
        with open(
            config.PROJECT_ROOT / "tests/data/node_deployer/create_img/load_template.pkl", "rb"
        ) as f:
            assert pickle.load(f) == template

    def test_apply_ignition_settings(self):
        with open(
            config.PROJECT_ROOT / "tests/data/node_deployer/create_img/load_template.pkl",
            mode="rb",
        ) as f:
            template = pickle.load(f)
        test_result = create_img.apply_ignition_settings(
            template,
            **TEST_PARAMS["create_img"]["apply_ignition_settings"],
        )
        with open(
            config.PROJECT_ROOT / "tests/data/node_deployer/create_img/apply_ignition_settings.pkl",
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
            config.PROJECT_ROOT / "tests/data/node_deployer/ignition.img",
        )


# class TestWriteDisk:
#     def init(self):
#         test_target = config.BUILD_DIR / "ignition.img"
#         if not test_target.exists():
#             test_target.write_bytes(
#                 Path(config.PROJECT_ROOT / "tests/data/node_deployer/ignition.img").read_bytes()
#             )

#     def test_validation_result(self):
#         raise NotImplementedError

#     def test_filter_validation_result(self):
#         raise NotImplementedError

#     def test_validate(self):
#         raise NotImplementedError
