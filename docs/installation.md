To install currently, download the `node_deployer` repo from the github repository, then install the package with poetry:
```bash
poetry install --no-dev
```
The tool can then be invoked with `poetry run node_deployer`. To install the tool system-wide, run `poetry build` and then install the package with `pip install dist/node_deployer*.whl`. The tool can then be invoked with `python -m node_deployer`.

This installation process will be subject to significant change in the future. Currently, the tool is in early alpha.