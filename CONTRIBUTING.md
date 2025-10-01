# Contributing to mediafile


First off, thanks for taking the time to contribute! ❤️

Please follow these guidelines to ensure a smooth contribution process.

## Pre-requisites

- Python 3.9 or higher
- Git

## Setup the Development Environment

1. Fork/Clone the repository on GitHub
```bash
git clone <your-fork-url>
cd mediafile
```
2. Install dependencies and set up the development environment
```bash
pip install -e .[dev]
```

## Before submitting a Pull Request

Verify that your code adheres to the project standards and conventions. Run
ruff and pytest to ensure your code is properly formatted and all tests pass.

```bash
ruff check .
ruff format .
pytest .
```
