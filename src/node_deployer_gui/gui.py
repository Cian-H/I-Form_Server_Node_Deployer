from collections import defaultdict
from functools import wraps
from pathlib import Path
from typing import Callable, DefaultDict, Optional, Tuple

import flet as ft
from node_deployer.create_disk import create_ignition_disk
from node_deployer.ip_interface import IPAddress

from .disk_dropdown import disk_dropdown
from .types import CreateDiskArgs


# Hotkeys will be mapped using using a dict to avoid a big, slow if-elif-else chain
def _no_hotkey() -> Callable[[ft.KeyboardEvent], None]:
    def dummy_func(e: ft.KeyboardEvent) -> None:
        pass

    return dummy_func


def optional_num_floordiv(num: ft.OptionalNumber, denom: int) -> Optional[int]:
    if num is None:
        return None
    elif isinstance(num, int):
        return num // denom
    else:
        return int(num / denom)


HOTKEY_MAP: DefaultDict[str, Callable[[ft.KeyboardEvent], None]] = defaultdict(_no_hotkey)


def main(page: ft.Page) -> None:
    page.title = "I-Form Server Node Deployer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # TODO: Add a progress bar
    # TODO: Add save/load functionality?

    # Lets start with the easiest part: a logo in the top left
    if page.platform_brightness == ft.ThemeMode.DARK:
        logo = ft.Image(str(Path(__file__).parent / "assets/logo_dark.png"), width=210)
    else:
        logo = ft.Image(str(Path(__file__).parent / "assets/logo_light.png"), width=210)

    logo_container = ft.Container(
        content=logo,
        padding=10,
        alignment=ft.alignment.top_left,
    )
    page.add(logo_container)

    # These fields are used to get the parameters for the disk creation
    disk, dd_element = disk_dropdown(tooltip="Select the disk to write to", label="Disk")
    hostname = ft.TextField(
        value="host",
        label="Hostname",
        text_align=ft.TextAlign.LEFT,
        width=optional_num_floordiv(page.window_width, 3)
    )
    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        text_align=ft.TextAlign.LEFT,
        width=hostname.width,
    )
    switch_ip = ft.TextField(
        label="Switch IP", text_align=ft.TextAlign.LEFT, width=hostname.width
    )
    switch_port = ft.TextField(
        label="Switch Port",
        value="4789",
        text_align=ft.TextAlign.LEFT,
        width=hostname.width,
    )
    swarm_token = ft.TextField(
        label="Swarm Token",
        text_align=ft.TextAlign.LEFT,
        width=(2*hostname.width) if hostname.width else None,
    )

    # Map varnames, as they will be useful for unpacking later
    varnames = {
        disk: "disk",
        hostname: "hostname",
        password: "password",
        switch_ip: "switch_ip",
        switch_port: "switch_port",
        swarm_token: "swarm_token",
    }

    # This wrapper validates the value of the field before passing it to the function
    def validate_value[F](func: Callable[[], F]) -> Callable[
        [], Optional[F]
    ]:  # mypy PEP 695 support can't come quickly enough # noqa
        #! It is important that bool(F) evaluates to False if the value is invalid
        @wraps(func)
        def wrapped() -> Optional[F]:
            out: F = func()
            if out:
                return out
            else:
                return None

        return wrapped

    # The following closures are used to get the values of the fields as the correct datatype
    @validate_value
    def get_disk() -> str:
        return disk.value if disk.value is not None else ""

    @validate_value
    def get_hostname() -> str:
        return hostname.value if hostname.value is not None else ""

    @validate_value
    def get_password() -> str:
        return password.value if password.value is not None else ""

    @validate_value
    def get_switch_ip() -> IPAddress:
        ip = IPAddress("0.0.0.0")
        try:
            ip = IPAddress(switch_ip.value)
        except ValueError:
            pass
        return ip

    @validate_value
    def get_switch_port() -> int:
        return int(switch_port.value if switch_port.value is not None else "0")

    @validate_value
    def get_swarm_token() -> str:
        return swarm_token.value if swarm_token.value is not None else ""

    # A bidirectional dictionary gives us a stateless bidirectional map between
    # fields and their fetch functions
    type FieldFetch = Tuple[ft.TextField | ft.Dropdown, Callable]
    field_fetch_map: Tuple[
        FieldFetch, FieldFetch, FieldFetch, FieldFetch, FieldFetch, FieldFetch
    ] = (
        (disk, get_disk),
        (hostname, get_hostname),
        (password, get_password),
        (switch_ip, get_switch_ip),
        (switch_port, get_switch_port),
        (swarm_token, get_swarm_token),
    )

    # This button triggers the confirmation popup before calling the disk creation function
    def confirm_disk_creation(*_) -> None:
        # Fetch the values of the fields
        vals: CreateDiskArgs = {
            "disk": "",
            "hostname": "",
            "password": "",
            "switch_ip": IPAddress("0.0.0.0"),
            "switch_port": 0,
            "swarm_token": "",
        }
        invalid_values = False
        for field, fetch_func in field_fetch_map:
            value = fetch_func()
            varname: str = varnames[field]
            if varname in CreateDiskArgs.__annotations__.keys():
                target_type = CreateDiskArgs.__annotations__[varname]
            else:
                raise KeyError(f"Field {varname} is not in CreateDiskArgs")
            if value is None:
                # If invalid values, highlight the field and set the error text
                field.error_text = "This field is required"
                field.border_color = "RED"
                field.update()
                invalid_values = True
            else:
                # If valid values, ensure the field is not highlighted and clear the error text
                field.error_text = None
                field.border_color = None
                field.update()
                typed_val = target_type(value)
                vals[varname] = typed_val  # type: ignore #! This is a false positive, an invalid literal would have been caught by the if statement above

        if invalid_values:
            return

        disk_val: str = vals["disk"]
        hostname_val: str = vals["hostname"]
        password_val: str = vals["password"]
        switch_ip_val: IPAddress = vals["switch_ip"]
        switch_port_val: int = vals["switch_port"]
        swarm_token_val: str = vals["swarm_token"]

        # The following closures build the confirmation popup
        # Also: nested closures, eww. It feels dirty, but maintains the functional style
        # and most of its benefits. I'm tempting the functional gods to punish me with
        # side-effects here though...
        def close_dlg(*_) -> None:
            dlg.open = False
            if "Y" in HOTKEY_MAP.keys():
                del HOTKEY_MAP["Y"]
            if "N" in HOTKEY_MAP.keys():
                del HOTKEY_MAP["N"]
            HOTKEY_MAP["Enter"] = confirm_disk_creation
            page.update()

        # This closure is called when the confirm disk creation button is pressed
        def trigger_disk_creation(*_) -> None:
            dlg.title = None
            dlg.content = ft.Row(
                controls=[
                    ft.Text("Creating disk..."),
                    ft.ProgressRing(),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
            dlg.actions = []
            page.update()
            create_ignition_disk(
                disk=disk_val,
                hostname=hostname_val,
                password=password_val,
                switch_ip=switch_ip_val,
                switch_port=switch_port_val,
                swarm_token=swarm_token_val,
            )
            dlg.content = ft.Text("Ignition disk created!")
            dlg.actions = [
                ft.TextButton("OK", on_click=close_dlg),
            ]
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text(f"Overwrite disk {disk_val}?"),
            actions=[
                ft.TextButton("Yes", on_click=trigger_disk_creation),
                ft.TextButton("No", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Finally, we open the dialog popup and switch the hotkeys over
        page.dialog = dlg
        dlg.open = True
        if "Enter" in HOTKEY_MAP.keys():
            del HOTKEY_MAP["Enter"]
        HOTKEY_MAP["Y"] = trigger_disk_creation
        HOTKEY_MAP["N"] = close_dlg
        page.update()


    disk_creation_dialog = ft.FilledButton(
        text="Create Ignition Disk",
        on_click=confirm_disk_creation,
        width=hostname.width,
    )

    # Then, we arrange the fields into rows and columns
    disk_row = ft.Row(
        controls=[
            dd_element,
            disk_creation_dialog,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    node_row = ft.Row(
        controls=[
            hostname,
            password,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    switch_row = ft.Row(
        controls=[
            switch_ip,
            switch_port,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    swarm_token_row = ft.Row(
        controls=[
            swarm_token,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    stacked_rows = ft.Column(
        [disk_row, node_row, switch_row, swarm_token_row],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Finally, we finish constructing the UI by adding the rows to the page
    page.add(stacked_rows)

    # As a final task, we define the opening screen hotkey events
    HOTKEY_MAP["Enter"] = confirm_disk_creation

    def quit_app(e: ft.KeyboardEvent) -> None:
        if e.ctrl:
            page.window_close()

    HOTKEY_MAP["Q"] = quit_app

    def on_key_press(e: ft.KeyboardEvent) -> None:
        HOTKEY_MAP[e.key](e)

    page.on_keyboard_event = on_key_press

    page.update()  # This shouldn't be necessary, but ensures the UI is rendered correctly
