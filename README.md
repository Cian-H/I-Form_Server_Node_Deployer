

## 

# I-Form Server Node Deployer
---
## Introduction
Welcome to the documentation for the I-Form Server Node Deployer tool. This tool is designed to simplify the process of deploying new nodes to the I-Form server swarm. It is intended to make the process of deploying new nodes as simple as possible, and to reduce the amount of time required to deploy new nodes. This should provide a reliable and consistent deployment process, creating an adaptable and scalable foundation for building research servers.
## Description
This program is designed to automatically create install media for deploying a swarm of minimal, immutable, and stateless nodes, to which containers can be deployed. If correctly configured, the resulting nodes will automatically connect to the specied swarm manager and immediately begin running deployed containers. The deployed nodes can be managed via the MicroOS dashboard, or via SSH. If the swarm is managed by a similarly deployed node, the entire swarm can also be managed via the MicroOS dashboard. Otherwise, access to the swarm manager is required to manage the swarm.
## Notice
The tool is currently in early alpha, and is subject to significant change.

## Installation

To install currently, download the `node_deployer` repo from the github repository, then install the package with poetry:
```bash
poetry install --no-dev
```
The tool can then be invoked with `poetry run node_deployer`. To install the tool system-wide, run `poetry build` and then install the package with `pip install dist/node_deployer*.whl`. The tool can then be invoked with `python -m node_deployer`.

This installation process will be subject to significant change in the future. Currently, the tool is in early alpha.

## Usage

To create an install disk invoke the `create-ignition-disk` command. The tool will then prompt the user to input the required parameters. Alternatively, the parameters can be passed as command line arguments. The following example creates an install disk on `/dev/sdb` managed by the computer at `192.168.1.1`
```bash
    node_deployer create-ignition-disk -d /dev/sdb -ip 192.168.1.1
```
The user will then be prompted to input a password and swarm token.

## Deployment

This tool creates an [ignition drive](https://coreos.github.io/ignition/) that can be used with a [OpenSUSE MicroOS self-install drive](https://get.opensuse.org/microos/) to automatically deploy new nodes to the swarm.