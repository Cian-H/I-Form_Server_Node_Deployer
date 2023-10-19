import time
import io
import tarfile
from pathlib import Path
import docker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CLIENT = docker.from_env()
SELENIUM_INIT_MESSAGE = "INFO [Standalone.execute] - Started Selenium Standalone"
FUELIGNITION_URL = "https://opensuse.github.io/fuel-ignition/edit"
CWD_MOUNTDIR = Path("/host_cwd")


def create_driver():
    driver = webdriver.Remote(
        "http://127.0.0.1:4444",
        options=webdriver.FirefoxOptions(),
    )
    driver.implicitly_wait(10)
    return driver


def convert_json_via_fuelignition(container, driver, fuel_ignition_json, img_path):
    driver.get(FUELIGNITION_URL)
    # Navigate to "Load Settings from" and upload the json
    load_from = driver.find_element(By.NAME, "load_from")
    load_from.send_keys(str(CWD_MOUNTDIR / fuel_ignition_json))
    # Walk through page structure to find, scroll to and click "Convert and Download"
    export = driver.find_element(By.ID, "export")
    export_divs = export.find_elements(By.TAG_NAME, "div")
    convert_div = export_divs[9]
    convert_button = convert_div.find_element(By.TAG_NAME, "button")
    # Ensure "Downloads" is empty if it exists
    container.exec_run(
        "[ -d /home/seluser/Downloads/* ] && rm /home/seluser/Downloads/*"
    )
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
    while (
        ".img.part" in container.exec_run("ls /home/seluser/Downloads/").output.decode()
    ):
        time.sleep(0.1)
    image_file = (
        container.exec_run("ls /home/seluser/Downloads/").output.decode().split()[0]
    )
    # Finally, fetch the image file from the container
    client_image_path = f"/home/seluser/Downloads/{image_file}"
    host_image_path = Path().cwd() / img_path
    if host_image_path.exists():
        host_image_path.unlink()
    filestream = container.get_archive(client_image_path)[0]
    # unpack the tarfile in memory
    bytestream = io.BytesIO(b''.join(chunk for chunk in filestream))
    bytestream.seek(0)
    tar = tarfile.open(fileobj=bytestream)
    with open(host_image_path, "wb+") as f:
        f.write(tar.extractfile(tar.getmembers()[0].name).read())


def json_to_img(fuel_ignition_json, img_path):
    selenium_container = None
    try:
        selenium_container = CLIENT.containers.run(
            "selenium/standalone-firefox:latest",
            detach=True,
            ports={4444: 4444, 7900: 7900},
            mounts=[
                docker.types.Mount(
                    target=str(CWD_MOUNTDIR),
                    source=str(Path.cwd().absolute()),
                    type="bind",
                )
            ],
        )
        # Wait for the container to finish starting up
        while SELENIUM_INIT_MESSAGE not in selenium_container.logs().decode():
            time.sleep(0.1)
        driver = create_driver()
        convert_json_via_fuelignition(
            selenium_container, driver, fuel_ignition_json, img_path
        )
        driver.quit()
    except Exception as e:
        raise e
    finally:
        selenium_container.stop()


if __name__ == "__main__":
    json_to_img("build/fuel-ignition.json", "build/ignition.img")
