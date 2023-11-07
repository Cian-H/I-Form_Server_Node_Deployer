# Configurations
The following is a list of preprogrammed configurations for the node deployer.
## default
This is the default configuration on which all other configurations are based.

| Variable | Value | Type |
| --- | --- | --- |
| SRC_DIR | "src" | Path |
| BUILD_DIR | "build" | Path |
| DOCKERFILE_DIR | "docker" | Path |
| SELENIUM_INIT_MESSAGE | "INFO [Standalone.execute] - Started Selenium Standalone" | str |
| FUELIGNITION_INIT_MESSAGE | "ready in *ms." | str |
| FUELIGNITION_URL | "http://localhost:3000/fuel-ignition/edit" | str |
| FUELIGNITION_BUILD_DIR | "fuel-ignition" | Path |
| CWD_MOUNTDIR | "/host_cwd" | Path |
| CLIENT_STDOUT | True | bool |
| CLEANUP_IMAGES | True | bool |
| CLI | False | bool |
| DEBUG | False | bool |
| TESTING | False | bool |

## local
This configuration keeps all computations local to the machine on which the tool is run.

| Variable | Value | Type |
| --- | --- | --- |
| FUELIGNITION_URL | "http://localhost:3000/fuel-ignition/edit" | str |

## remote
<p>This configuration allows the use of hosted websites for hte fuel-ignition configurator.</p>
<p>Currently, this configuration is broken/deprecated. It is being kept as it may be be reimplemented in the future as part of a dockerless configuration.</p>

| Variable | Value | Type |
| --- | --- | --- |
| FUELIGNITION_URL | "https://opensuse.github.io/fuel-ignition/edit" | str |

## cli
This configuration enables a typer based command line interface.

| Variable | Value | Type |
| --- | --- | --- |
| CLI | True | bool |

## debug
This configuration enables debug mode.

| Variable | Value | Type |
| --- | --- | --- |
| DEBUG | True | bool |
| CLI | False | bool |
| CLEANUP_IMAGES | False | bool |

## test
This configuration enables testing mode. This mode is used for testing the tool itself.

| Variable | Value | Type |
| --- | --- | --- |
| TESTING | True | bool |
| CLEANUP_IMAGES | False | bool |