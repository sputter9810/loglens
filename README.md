# LogLens

LogLens is a Python command-line application for analysing local HTTP server access logs. It is intended to make large text logs easier to inspect through structured parsing, filtering and summaries.

This repository currently contains the installable package foundation. Log parsing and CLI commands are not part of this issue and will be added in later work.

## Portfolio standards

The portfolio engineering standards used for this project are kept in [`docs/standards/`](docs/standards/). This is a project-local snapshot; it is not automatically synchronized with the shared standards repository.

## Requirements

- Python 3.12 or newer

## Development setup

From the repository root, run these commands in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

The commands use the virtual environment's interpreter directly, so activating it is not required. The editable install makes changes under `src/` importable without reinstalling the package. The project uses setuptools as its standard, lightweight PEP 517 build backend. Pytest provides the initial package smoke test; Ruff supplies a focused Python linter for development checks. These tools are development-only and there are no runtime dependencies.

## Checks

Run the tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run the linter with:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

## Licence

Sam's licence decision is pending. No licence has been selected or granted yet.