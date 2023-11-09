from functools import wraps
from typing import Callable, Mapping

from bidict import frozenbidict
import flet as ft
from flet_core.form_field_control import FormFieldControl
from node_deployer.create_disk import create_ignition_disk
from node_deployer.ip_interface import IPAddress

from .disk_dropdown import disk_dropdown


def main(page: ft.Page) -> None:
    page.title = "I-Form Server Node Deployer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

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

    # This wrapper validates the value of the field before passing it to the function
    def validate_value(func: Callable) -> Callable:
        @wraps(func)
        def wrapped():
            out = func()
            if out:
                return out
            else:
                # TODO: Highlight the invalid field
                raise NotImplementedError("Invalid field value path not implemented")

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
        return IPAddress(switch_ip.value if switch_ip.value is not None else "0.0.0.0")

    @validate_value
    def get_switch_port() -> int:
        return int(switch_port.value if switch_port.value is not None else "0")

    @validate_value
    def get_swarm_token() -> str:
        return swarm_token.value if swarm_token.value is not None else ""

    # A bidirectional dictionary gives us a stateless bidirectional map between
    # fields and their fetch functions
    field_fetch_map: Mapping[FormFieldControl, Callable] = frozenbidict(
        {
            disk: get_disk,
            hostname: get_hostname,
            password: get_password,
            switch_ip: get_switch_ip,
            switch_port: get_switch_port,
            swarm_token: get_swarm_token,
        }
    )

    # This button triggers the confirmation popup before calling the disk creation function
    def confirm_disk_creation(*_):
        # Fetch the values of the fields
        disk_val: str = field_fetch_map[disk]()
        hostname_val: str = field_fetch_map[hostname]()
        password_val: str = field_fetch_map[password]()
        switch_ip_val: IPAddress = field_fetch_map[switch_ip]()
        switch_port_val: int = field_fetch_map[switch_port]()
        swarm_token_val: str = field_fetch_map[swarm_token]()

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
            close_dlg(None)

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
