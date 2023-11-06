# node_deployer

A tool for creating ignition images for automated deployment to a swarm

## Options

| **Option** | **Description** |
|----|----|
| --install-completion | Install completion for the current shell. |
| --show-completion | Show completion for the current shell, to copy it or customize the installation. |

## Commands

| **Command** | **Description** |
|----|----|
| create-ignition-disk | Creates an ignition image and writes it to the specified disk |
| create-img | Creates an ignition image for a node that will automatically join a swarm |
| json-to-img | Converts a fuel-ignition json file to an ignition disk image file |
                                                                                                                            
### create-ignition-disk
Creates an ignition image and writes it to the specified disk

| Argument | Description | Default |
|----|----|----|
| --disk  -d | Path to the disk to write to | None |
| --hostname  -h | Hostname for the new node | node |
| --password  -p | Password for the root user on the new node | None |
| --switch-ip  -ip | IP address of the switch to connect to | None |
| --switch-port  -sp | Port on the switch to connect | 4789 |
| --swarm-token  -t | Swarm token for connecting to the swarm | None |

### create-img
Creates an ignition image for a node that will automatically join a swarm

| Argument | Description | Default |
|----|----|----|
| --hostname  -h | Hostname for the new node | node |
| --password  -p | Password for the root user on the new node | None |
| --switch-ip  -ip | IP address of the switch to connect to | None |
| --switch-port  -sp | Port on the switch to connect to | 4789 |
| --swarm-token  -t | Swarm token for connecting to the swarm | None |
| --img-path  -o | Path to which the ignition image should be written | ignition.img |

### json-to-img
Converts a fuel-ignition json file to an ignition disk image file

| Argument | Description | Default |
|----|----|----|
| --json-path  -i | The fuel-ignition json for configuring the disk image | fuelignition.json |
| --img-path  -o | The file to output the disk image to | ignition.img |