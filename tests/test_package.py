from importlib.metadata import version
from pathlib import Path

import loglens


def test_package_import_and_editable_install_metadata() -> None:
    source_directory = Path(__file__).parents[1] / "src"

    assert loglens.__file__ is not None
    assert Path(loglens.__file__).resolve().is_relative_to(source_directory.resolve())
    assert version("loglens") == "0.1.0"
