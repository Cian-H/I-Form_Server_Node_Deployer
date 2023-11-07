import flet as ft
import psutil
from typing import Tuple


def get_disk_options() -> list[ft.dropdown.Option]:
    physical_disks = list(filter(lambda x: "loop" not in x.device, psutil.disk_partitions()))
    disks = [
        ft.dropdown.Option(
            key=disk.device,
            text=f"{disk.device} ({disk.mountpoint})",
        )
        for disk in physical_disks
    ]
    return disks


def disk_dropdown(**kwargs) -> Tuple[ft.Dropdown, ft.Row]:
    dropdown = ft.Dropdown(
        options=get_disk_options(),
        **kwargs,
    )
    
    def refresh_dropdown(_):
        dropdown.options = get_disk_options()
        dropdown.update()
    
    refresh_button = ft.IconButton(
        icon="refresh",
        tooltip="Refresh disk list",
        on_click=refresh_dropdown,
    )
    element = ft.Row(
        controls=[dropdown, refresh_button],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    return dropdown, element