from telnetlib import IP
import flet as ft
from httpx import get
from node_deployer.create_disk import IPAddress, create_ignition_disk
import ipaddress

from .disk_dropdown import disk_dropdown


def main(page: ft.Page) -> None:
    page.title = "I-Form Server Node Deployer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    #TODO: Add a confirmation before actually writing to the disk
    #TODO: Add a private password field
    #TODO: Add a guard against invalid values
    #TODO: Guard should trigger highlighting of the invalid fields
    #TODO: Add a progress bar
    #TODO: Finalise arrangement of fields
    
    disk, dd_element = disk_dropdown(tooltip="Select the disk to write to", label="Disk")
    hostname = ft.TextField(value="host", label="Hostname", text_align=ft.TextAlign.LEFT)
    password = ft.TextField(label="Password", text_align=ft.TextAlign.LEFT)
    switch_ip = ft.TextField(label="Switch IP", text_align=ft.TextAlign.LEFT)
    switch_port = ft.TextField(label="Switch Port", value="4789", text_align=ft.TextAlign.LEFT)
    swarm_token = ft.TextField(label="Swarm Token", text_align=ft.TextAlign.LEFT)
    
    def get_disk() -> str:
        return disk.value if disk.value is not None else ""

    def get_hostname() -> str:
        return hostname.value if hostname.value is not None else ""
    
    def get_password() -> str:
        return password.value if password.value is not None else ""
    
    def get_switch_ip() -> IPAddress:
        return ipaddress.ip_address(switch_ip.value if switch_ip.value is not None else "0.0.0.0")
    
    def get_switch_port() -> int:
        return int(switch_port.value if switch_port.value is not None else "0")
    
    def get_swarm_token() -> str:
        return swarm_token.value if swarm_token.value is not None else ""
    
    def trigger_disk_creation(_):
        raise NotImplementedError
        create_ignition_disk(
            disk=get_disk(),
            hostname=get_hostname(),
            password=get_password(),
            switch_ip=get_switch_ip(),
            switch_port=get_switch_port(),
            swarm_token=get_swarm_token(),
        )

    disk_row = ft.Row(
        controls=[
            dd_element,
            ft.FilledButton(
                text="Create Ignition Disk",
                on_click=trigger_disk_creation, 
            ),
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
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    page.add(
        ft.Column(
            [disk_row, node_row, switch_row, swarm_token],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )