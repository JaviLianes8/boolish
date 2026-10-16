"""Real end to end: build the archives, install the wheel, drive it as a consumer.

Slow and online (it creates virtual environments and installs boolish 0.1.0 from PyPI),
so it only runs with ``BOOLISH_E2E=1``. No mocks: the installed console script and
``python -m boolish`` are run by subprocess and their stdout, stderr and exit codes read.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("BOOLISH_E2E") != "1", reason="BOOLISH_E2E=1")
ROOT = Path(__file__).resolve().parent.parent
BIN = "Scripts" if sys.platform == "win32" else "bin"
EXE = ".exe" if sys.platform == "win32" else ""


def _run(*args: object, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [str(arg) for arg in args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=check,
        timeout=600,
    )


@pytest.fixture(scope="module")
def dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    _run(sys.executable, "-m", "build", "--outdir", out, ROOT)
    _run(sys.executable, "-m", "twine", "check", "--strict", *sorted(out.iterdir()))
    return out


def _venv(where: Path) -> Path:
    venv.create(where, with_pip=True)
    return where / BIN / f"python{EXE}"


def test_archives_hold_exactly_what_they_should(dist: Path) -> None:
    wheel = next(dist.glob("boolish-1.0.0-py3-none-any.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    package = {name for name in names if name.startswith("boolish/")}
    assert {"boolish/py.typed", "boolish/__init__.py", "boolish/__main__.py"} <= package
    assert all(name.endswith((".py", "py.typed")) for name in package)
    assert "boolish-1.0.0.dist-info/licenses/LICENSE" in names
    assert not [name for name in names if "test" in name or "script" in name]
    sdist = next(dist.glob("boolish-1.0.0.tar.gz"))
    with tarfile.open(sdist) as archive:
        members = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
    assert {"LICENSE", "README.md", "GUIDE.md", "CHANGELOG.md", "pyproject.toml"} <= members
    assert "tests/fixtures/oracles.json" in members
    sources = {name for name in members if name.startswith("tests/sources/")}
    assert sources == {"tests/sources/MANIFEST.json"}
    assert not [name for name in members if "cache" in name or name.startswith(".")]


def test_the_installed_wheel_works_for_a_consumer(dist: Path, tmp_path: Path) -> None:
    python = _venv(tmp_path / "env")
    _run(python, "-m", "pip", "install", "--quiet", next(dist.glob("*.whl")))
    cli = tmp_path / "env" / BIN / f"boolish{EXE}"
    for argv, code, out in [
        (["yes"], 0, "true\n"),
        (["off"], 1, "false\n"),
        (["--quiet", "1"], 0, ""),
        (["--lenient", "--rules", "multilingual", "Sí"], 0, "true\n"),
        (["--true", "aye", "--false", "nay", "nay"], 1, "false\n"),
        (["--version"], 0, "boolish 1.0.0\n"),
    ]:
        for command in ([cli], [python, "-m", "boolish"]):
            result = _run(*command, *argv, check=False)
            assert (result.returncode, result.stdout, result.stderr) == (code, out, ""), argv
    bad = _run(cli, "banana", check=False)
    assert (bad.returncode, bad.stdout) == (2, "")
    assert bad.stderr == "boolish: 'banana' is not a recognised boolean\n"
    snippet = "import boolish; print(boolish.to_bool(1), boolish.strtobool('no'), boolish.__file__)"
    printed = _run(python, "-c", snippet).stdout.split()
    assert printed[:2] == ["True", "False"]
    assert str(tmp_path) in printed[2]


def test_upgrade_in_place_from_pypi_0_1_0(dist: Path, tmp_path: Path) -> None:
    python = _venv(tmp_path / "env")
    _run(python, "-m", "pip", "install", "--quiet", "boolish==0.1.0")
    old = "import boolish; print(boolish.__version__, boolish.strtobool('enabled', None))"
    assert _run(python, "-c", old).stdout.split() == ["0.1.0", "None"]
    _run(python, "-m", "pip", "install", "--quiet", "--upgrade", next(dist.glob("*.whl")))
    assert _run(python, "-m", "pip", "check").returncode == 0
    new = (
        "import boolish; print(boolish.__version__, boolish.strtobool('enabled', None),"
        " boolish.strtobool('enabled', None, rules=boolish.CLASSIC))"
    )
    assert _run(python, "-c", new).stdout.split() == ["1.0.0", "True", "None"]
    listed = _run(python, "-m", "pip", "show", "-f", "boolish").stdout
    assert "boolish/_cli.py" in listed.replace("\\", "/")
