"""Real end to end test: install the package and drive the installed console script.

No mocks. A throwaway virtual environment is created, ``boolish`` is pip-installed into
it (editable), and the real ``boolish`` executable is run over ``subprocess``. The test
asserts the actual stdout, stderr and exit codes on real inputs.
"""

from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _scripts_dir(env_dir: Path) -> Path:
    return env_dir / ("Scripts" if sys.platform == "win32" else "bin")


def _exe(env_dir: Path, name: str) -> Path:
    suffix = ".exe" if sys.platform == "win32" else ""
    return _scripts_dir(env_dir) / f"{name}{suffix}"


@pytest.fixture(scope="module")
def boolish_cli(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a venv, install boolish into it, and return the console script path."""
    env_dir = tmp_path_factory.mktemp("boolish-e2e-venv")
    venv.create(env_dir, with_pip=True)
    python = _exe(env_dir, "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
        check=True,
        capture_output=True,
        timeout=300,
    )
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "-e", str(PROJECT_ROOT)],
        check=True,
        capture_output=True,
        timeout=600,
    )
    cli = _exe(env_dir, "boolish")
    assert cli.is_file(), f"console script was not installed at {cli}"
    return cli


def _run(cli: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(cli), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_installed_script_reports_true(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "yes")
    assert result.returncode == 0
    assert result.stdout.strip() == "true"
    assert result.stderr == ""


def test_installed_script_reports_false(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "off")
    assert result.returncode == 1
    assert result.stdout.strip() == "false"


def test_installed_script_errors_to_stderr(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "banana")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "banana" in result.stderr


def test_installed_script_quiet_uses_exit_code_only(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "--quiet", "1")
    assert result.returncode == 0
    assert result.stdout == ""


def test_installed_script_lenient_multilingual(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "--lenient", "--rules", "multilingual", "Sí")
    assert result.returncode == 0
    assert result.stdout.strip() == "true"


def test_installed_script_custom_words(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "--true", "aye", "--false", "nay", "nay")
    assert result.returncode == 1
    assert result.stdout.strip() == "false"


def test_installed_script_reports_version(boolish_cli: Path) -> None:
    result = _run(boolish_cli, "--version")
    assert result.returncode == 0
    assert result.stdout.strip().startswith("boolish ")


def test_installed_package_is_importable_and_coerces(boolish_cli: Path) -> None:
    python = _exe(boolish_cli.parent.parent, "python")
    result = subprocess.run(
        [str(python), "-c", "import boolish; print(boolish.to_bool(1), boolish.strtobool('no'))"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "True False"
