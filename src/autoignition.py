from fnmatch import fnmatch
import io
import tarfile
import time
from typing import Annotated

import git
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import typer

from cli import cli_spinner
import config
from debug import debug_guard
from utils import ensure_build_dir


def create_driver():
    driver = webdriver.Remote(
        "http://127.0.0.1:4444",
        options=webdriver.FirefoxOptions(),
    )
    driver.implicitly_wait(10)
    return driver


def convert_json_via_fuelignition(container, driver, fuelignition_json, img_path):
    driver.get(config.FUELIGNITION_URL)
    # Navigate to "Load Settings from" and upload the json
    load_from = driver.find_element(By.NAME, "load_from")
    load_from.send_keys(str(config.CWD_MOUNTDIR / fuelignition_json))
    # Walk through page structure to find, scroll to and click "Convert and Download"
    export = driver.find_element(By.ID, "export")
    export_divs = export.find_elements(By.TAG_NAME, "div")
    convert_div = export_divs[9]
    convert_button = convert_div.find_element(By.TAG_NAME, "button")
    # Ensure "Downloads" is empty if it exists
    container.exec_run("[ -d /home/seluser/Downloads/* ] && rm /home/seluser/Downloads/*")
    # A hacky way of scrolling to the element, but is only way i can find right now
    convert_button.location_once_scrolled_into_view
    time.sleep(1)
    w = WebDriverWait(driver, 10)
    w.until_not(EC.invisibility_of_element(convert_button))
    w.until(EC.element_to_be_clickable(convert_button))
    convert_button.click()
    # Now, wait for the file to be downloaded
    while container.exec_run("ls /home/seluser/Downloads/").exit_code != 0:
        time.sleep(0.1)
    while ".img.part" in container.exec_run("ls /home/seluser/Downloads/").output.decode():
        time.sleep(0.1)
    image_file = container.exec_run("ls /home/seluser/Downloads/").output.decode().split()[0]
    # Finally, fetch the image file from the container
    client_image_path = f"/home/seluser/Downloads/{image_file}"
    host_image_path = config.ROOT_DIR / img_path
    if host_image_path.exists():
        host_image_path.unlink()
    filestream = container.get_archive(client_image_path)[0]
    # unpack the tarfile in memory
    bytestream = io.BytesIO(b"".join(chunk for chunk in filestream))
    bytestream.seek(0)
    tar = tarfile.open(fileobj=bytestream)
    with open(host_image_path, "wb+") as f:
        f.write(tar.extractfile(tar.getmembers()[0].name).read())


def build_fuelignition():
    # Make sure the local fuel-ignition repo is up to date
    if (not config.FUELIGNITION_BUILD_DIR.exists()) or (
        len(tuple(config.FUELIGNITION_BUILD_DIR.iterdir())) == 0
    ):
        repo = git.Repo.clone_from(
            "https://github.com/openSUSE/fuel-ignition.git",
            config.FUELIGNITION_BUILD_DIR,
            branch="main",
        )
    else:
        repo = git.Repo(config.FUELIGNITION_BUILD_DIR)
    repo.remotes.origin.update()
    repo.remotes.origin.pull()
    # Then, build the docker image using the Dockerfile in the repo
    # * For the container to build, we need to use a patched Dockerfile
    # * The patch manually creates a "fuelignition" usergroup
    # * From reading up, this change to how docker creates usergroups
    # * appears to have been introduced in engine version 9.3.0 and above?
    # * For now, we're applying the patch @>=9.3.0 and can change later if needed
    engine_version = tuple(
        map(
            int,
            next(
                filter(lambda x: x.get("Name") == "Engine", config.CLIENT.version()["Components"])
            )["Version"].split("."),
        )
    )
    root_container = (engine_version[0] > 9) or (engine_version[0] == 9 and engine_version[1] >= 3)
    dockerfile = "Dockerfile"
    if root_container:
        dockerfile = config.DOCKERFILE_DIR / "fuel-ignition.dockerfile"
    image, _ = config.CLIENT.images.build(
        path=str(config.FUELIGNITION_BUILD_DIR),
        dockerfile=str(dockerfile),
        tag="fuel-ignition",
        network_mode="host",
        buildargs={"CONTAINER_USERID": "1000"},
        pull=True,
        quiet=True,
        rm=config.CLEANUP_IMAGES,
    )
    return image


@debug_guard
@cli_spinner(description="Converting json to img", total=None)
@ensure_build_dir
def json_to_img(
    fuelignition_json: Annotated[
        str, typer.Option(help="The fuel-ignition json for configuring the disk image", prompt=True)
    ],
    img_path: Annotated[
        str, typer.Option(help="The file to output the disk image to", prompt=True)
    ],
) -> None:
    """Takes a fuel-ignition json file and produces an ignition disk image file"""
    selenium_container = None
    fuelignition_container = None
    fuelignition_image = None
    try:
        # Initialise containers
        selenium_container = config.CLIENT.containers.run(
            "selenium/standalone-firefox:latest",
            detach=True,
            remove=True,
            ports={4444: 4444, 7900: 7900},
            mounts=[
                config.CWD_MOUNT,
            ],
        )
        fuelignition_image = build_fuelignition()
        fuelignition_container = config.CLIENT.containers.run(
            fuelignition_image,
            detach=True,
            remove=True,
            network_mode=f"container:{selenium_container.id}",
        )
        # Wait for the containers to finish starting up
        while config.SELENIUM_INIT_MESSAGE not in selenium_container.logs().decode():
            time.sleep(0.1)
            for event in config.CLIENT.events(decode=True):
                print(event)
        while not fnmatch(
            fuelignition_container.logs().decode().strip().split("\n")[-1].strip(),
            config.FUELIGNITION_INIT_MESSAGE,
        ):
            time.sleep(0.1)
        # Now, create the webdriver and convert the json to an img
        driver = create_driver()
        convert_json_via_fuelignition(selenium_container, driver, fuelignition_json, img_path)
        driver.quit()
    except Exception as e:
        raise e
    finally:
        if selenium_container is not None:
            selenium_image = selenium_container.image
            selenium_container.kill()
            if config.CLEANUP_IMAGES:
                selenium_image.remove(force=True)
        if fuelignition_container is not None:
            fuelignition_container.kill()
        if fuelignition_image is not None:
            if config.CLEANUP_IMAGES:
                fuelignition_image.remove(force=True)


if __name__ == "__main__":
    config.update_config("cli")
    typer.run(json_to_img)
