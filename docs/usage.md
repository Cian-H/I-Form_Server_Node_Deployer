To create an install disk invoke the `create-ignition-disk` command. The tool will then prompt the user to input the required parameters. Alternatively, the parameters can be passed as command line arguments. The following example creates an install disk on `/dev/sdb` managed by the computer at `192.168.1.1`
```bash
    node_deployer create-ignition-disk -d /dev/sdb -ip 192.168.1.1
```
The user will then be prompted to input a password and swarm token.