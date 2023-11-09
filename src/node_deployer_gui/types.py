from typing import TypedDict

from node_deployer.ip_interface import IPAddress


class CreateDiskArgs(TypedDict):
    disk: str
    hostname: str
    password: str
    switch_ip: IPAddress
    switch_port: int
    swarm_token: str
