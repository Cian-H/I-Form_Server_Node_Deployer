import flet as ft


def main(page: ft.Page) -> None:
    page.title = "I-Form Server Node Deployer"
    
    #TODO: change this test code to the actual gui
    #   Should basically be a simple wrapper around the node_deployer.py CLI
    #   Should have a file browser for selecting files
    #   Should have a selector for choosing the disk to write to
    #   Should have checks to ensure valid input
    #   Should have a progress bar or similar to show progress
    #   Intended to be idiot-proof, so anyone can use it
    #   Needs solid error handling and bulletproof documentation/testing


ft.app(target=main)