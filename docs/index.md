# I-Form Server Node Deployer
---
## Introduction
Welcome to the documentation for the I-Form Server Node Deployer tool. This tool is designed to simplify the process of deploying new nodes to the I-Form server swarm. It is intended to make the process of deploying new nodes as simple as possible, and to reduce the amount of time required to deploy new nodes. This should provide a reliable and consistent deployment process, creating an adaptable and scalable foundation for building research servers.
## Description
This program is designed to automatically create install media for deploying a swarm of minimal, immutable, and stateless nodes, to which containers can be deployed. If correctly configured, the resulting nodes will automatically connect to the specied swarm manager and immediately begin running deployed containers. The deployed nodes can be managed via the MicroOS dashboard, or via SSH. If the swarm is managed by a similarly deployed node, the entire swarm can also be managed via the MicroOS dashboard. Otherwise, access to the swarm manager is required to manage the swarm.
## Notice
The tool is currently in early alpha, and is subject to significant change.