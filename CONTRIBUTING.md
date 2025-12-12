# Contributing to mediafile

First off, thanks for taking the time to contribute! ❤️

Please follow these guidelines to ensure a smooth contribution process.

## Pre-requisites

- Python 3.10 or higher
- Git

## Setup the Development Environment

1. Fork/Clone the repository on GitHub

```bash
$ git clone <your-fork-url>
$ cd mediafile
```

We use `uv` to manage virtual environments. If you don't have it installed, see [here](https://pypi.org/project/uv/).

2. Install dependencies and set up the development environment (using same lockfile as production):
```bash
uv sync --frozen --group dev
```

3. Activate the virtual environment managed by `uv`:
```bash
source .venv/bin/activate
```

## Before submitting a Pull Request

Verify that your code adheres to the project standards and conventions. Run
ruff and pytest to ensure your code is properly formatted and all tests pass.

```bash
$ poe lint
$ poe format
$ poe test
```
