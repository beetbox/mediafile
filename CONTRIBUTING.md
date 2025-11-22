# Contributing to mediafile

First off, thanks for taking the time to contribute! ❤️

Please follow these guidelines to ensure a smooth contribution process.

## Pre-requisites

- Python 3.9 or higher
- Git

## Setup the Development Environment

We recommend using a virtual environment to manage dependencies. You can use `venv`, `conda`, or any other tool of your choice.

1. Fork/Clone the repository on GitHub

```bash
$ git clone <your-fork-url>
$ cd mediafile
```

2. Set up your development environment

```bash
$ python -m pip install --user pipx
$ pipx install poetry poethepoet
```

3. Install project dependencies

```bash
$ poetry install
```

## Before submitting a Pull Request

Verify that your code adheres to the project standards and conventions. Run
ruff and pytest to ensure your code is properly formatted and all tests pass.

```bash
$ poe lint
$ poe format
$ poe test
```
