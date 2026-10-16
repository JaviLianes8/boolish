"""Repository hygiene: file sizes, characters and the metadata the wheel is built from."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "dist", "build", "sources", "__pycache__"}
LONG_DASH = chr(0x2014)


def _files(*suffixes: str) -> list[Path]:
    found = []
    for path in ROOT.rglob("*"):
        parts = set(path.relative_to(ROOT).parts)
        hidden = any(part.startswith(".") for part in parts)
        if path.is_file() and path.suffix in suffixes and not parts & SKIP and not hidden:
            found.append(path)
    return found


def test_source_test_and_script_files_stay_under_200_lines() -> None:
    files = _files(".py", ".ps1")
    assert len(files) > 10
    for path in files:
        assert len(path.read_text("utf-8").splitlines()) <= 200, path


def test_no_long_dash_anywhere() -> None:
    for path in _files(".py", ".ps1", ".md", ".toml", ".json", ".txt", ".cfg"):
        assert LONG_DASH not in path.read_text("utf-8"), path


def test_the_package_has_no_runtime_dependencies() -> None:
    text = (ROOT / "pyproject.toml").read_text("utf-8")
    assert "\ndependencies = []\n" in text
    imports = set()
    for path in (ROOT / "src" / "boolish").glob("*.py"):
        for line in path.read_text("utf-8").splitlines():
            if line.startswith(("import ", "from ")):
                imports.add(line.split()[1].split(".")[0])
    assert imports <= {
        "__future__",
        "argparse",
        "boolish",
        "collections",
        "dataclasses",
        "math",
        "os",
        "sys",
        "typing",
        "unicodedata",
    }
