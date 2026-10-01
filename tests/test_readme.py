"""Keep documented command transcripts aligned with the tracked samples."""

import re
from pathlib import Path

import pytest

from loglens.cli import main

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("heading", ["Summary", "Filter", "Top paths", "Top IPs"])
def test_readme_transcript(heading, monkeypatch, capsys):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split(f"### {heading} example\n", 1)[1].split("\n### ", 1)[0]
    command = re.search(r"```powershell\n(.+)\n```", section).group(1)
    args = command.split()[1:]
    assert (ROOT / args[1]).is_file(), "Example must name a tracked sample"
    expected = re.findall(r"```text\n(.*?)```", section, flags=re.DOTALL)
    monkeypatch.chdir(ROOT)

    assert main(args) == 0
    captured = capsys.readouterr()
    assert captured.out == expected[0]
    assert captured.err == (expected[1] if len(expected) > 1 else "")
