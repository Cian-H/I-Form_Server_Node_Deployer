from functools import wraps
from typing import Callable, Optional, Tuple

import flet as ft
from node_deployer.create_disk import create_ignition_disk
from node_deployer.ip_interface import IPAddress

from .disk_dropdown import disk_dropdown
from .types import CreateDiskArgs


def main(page: ft.Page) -> None:
    page.title = "I-Form Server Node Deployer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # TODO: Add hotkeys
    # TODO: Add a logo
    # TODO: Add a progress bar
    # TODO: Finalise arrangement of fields

    # These fields are used to get the parameters for the disk creation
    disk, dd_element = disk_dropdown(tooltip="Select the disk to write to", label="Disk")
    hostname = ft.TextField(value="host", label="Hostname", text_align=ft.TextAlign.LEFT)
    password = ft.TextField(
        label="Password", password=True, can_reveal_password=True, text_align=ft.TextAlign.LEFT
    )
    switch_ip = ft.TextField(label="Switch IP", text_align=ft.TextAlign.LEFT)
    switch_port = ft.TextField(label="Switch Port", value="4789", text_align=ft.TextAlign.LEFT)
    swarm_token = ft.TextField(label="Swarm Token", text_align=ft.TextAlign.LEFT)
    
    # Add varnames, as they will be useful for unpacking later
    disk.__varname__ = "disk"
    hostname.__varname__ = "hostname"
    password.__varname__ = "password"
    switch_ip.__varname__ = "switch_ip"
    switch_port.__varname__ = "switch_port"
    swarm_token.__varname__ = "swarm_token"

    # This wrapper validates the value of the field before passing it to the function
    def validate_value[F](func: Callable[[], F]) -> Callable[[], Optional[F]]:  # mypy PEP 695 support can't come quickly enough # noqa
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
            varname: str = str(field.__varname__)
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
                vals[varname] = typed_val # type: ignore #! This is a false positive, an invalid literal would have been caught by the if statement above
        
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

        # Finally, we open the dialog popup
        page.dialog = dlg
        dlg.open = True
        page.update()

    disk_creation_dialog = ft.FilledButton(
        text="Create Ignition Disk",
        on_click=confirm_disk_creation,
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

    stacked_rows = ft.Column(
        [disk_row, node_row, switch_row, swarm_token],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Finally, we add the rows to the page
    page.add(stacked_rows)
