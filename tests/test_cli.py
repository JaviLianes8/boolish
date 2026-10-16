"""Unit tests for the argparse command line interface."""

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from boolish._cli import main

SRC = Path(__file__).resolve().parent.parent / "src"


def test_true_value_prints_true_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["yes"])
    assert code == 0
    assert capsys.readouterr().out == "true\n"


def test_false_value_prints_false_and_exits_one(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["off"])
    assert code == 1
    assert capsys.readouterr().out == "false\n"


def test_quiet_prints_nothing_but_keeps_the_exit_code(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--quiet", "on"]) == 0
    assert main(["--quiet", "0"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""


def test_unrecognised_value_goes_to_stderr_and_exits_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main(["banana"])
    assert code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "banana" in captured.err
    assert captured.err.startswith("boolish:")


def test_lenient_folds_accents(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--lenient", "--rules", "multilingual", "Sí"]) == 0
    assert capsys.readouterr().out == "true\n"


def test_strict_rejects_accents(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--rules", "multilingual", "Sí"]) == 2
    assert "Sí" in capsys.readouterr().err


def test_multilingual_vocabulary(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--rules", "multilingual", "oui"]) == 0
    assert capsys.readouterr().out == "true\n"


def test_custom_words(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--true", "aye", "--false", "nay", "aye"]) == 0
    assert capsys.readouterr().out == "true\n"
    assert main(["--true", "aye", "--false", "nay", "nay"]) == 1
    assert capsys.readouterr().out == "false\n"


def test_version_prints_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "boolish" in capsys.readouterr().out


def test_help_lists_runnable_examples(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "examples:" in out
    assert "boolish yes" in out
    assert "--lenient" in out


def test_clashing_custom_words_are_an_error_with_exit_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--true", "no", "yes"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "boolish: words marked both true and false: 'no'\n"


def test_usage_errors_exit_two(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in ([], ["--rules", "klingon", "yes"], ["--strict", "--lenient", "yes"], ["a", "b"]):
        with pytest.raises(SystemExit) as exc:
            main(argv)
        assert exc.value.code == 2
    assert capsys.readouterr().out == ""


def test_the_error_message_is_one_bounded_line(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["x" * 100_000]) == 2
    err = capsys.readouterr().err
    assert err == "boolish: '" + "x" * 32 + "'... is not a recognised boolean\n"


def test_classic_rules_and_repeated_words(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--rules", "classic", "enabled"]) == 2
    assert main(["--true", "aye", "--true", "yarr", "--false", "nay", "YARR"]) == 0
    assert main(["--rules", "classic", "--false", "nope", "nope"]) == 1
    assert capsys.readouterr().out == "true\nfalse\n"


def test_output_survives_a_stream_that_cannot_encode(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = io.TextIOWrapper(io.BytesIO(), encoding="ascii", newline="\n")
    monkeypatch.setattr(sys, "stderr", stream)
    assert main(["--rules", "multilingual", "Sí\u202e"]) == 2
    stream.flush()
    written = stream.buffer.getvalue()
    assert written == b"boolish: 'S\\xed\\u202e' is not a recognised boolean\n"


def test_python_dash_m_runs_the_same_interface() -> None:
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONIOENCODING": "utf-8"}
    run = subprocess.run(
        [sys.executable, "-m", "boolish", "--lenient", "--rules", "multilingual", "NÃO"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
    )
    assert (run.returncode, run.stdout, run.stderr) == (1, "false\n", "")
    bad = subprocess.run(
        [sys.executable, "-m", "boolish", "maybe"], capture_output=True, text=True, env=env
    )
    assert (bad.returncode, bad.stdout) == (2, "")
    assert bad.stderr.strip() == "boolish: 'maybe' is not a recognised boolean"


class ClosedPipe(io.StringIO):
    """A stdout whose reader has gone away."""

    def __init__(self, fd: int) -> None:
        super().__init__()
        self.fd = fd

    def write(self, text: str) -> int:
        raise BrokenPipeError(32, "Broken pipe")

    def fileno(self) -> int:
        return self.fd


def test_a_closed_output_pipe_keeps_the_exit_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = tmp_path / "out.txt"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT)
    try:
        monkeypatch.setattr(sys, "stdout", ClosedPipe(fd))
        assert main(["yes"]) == 0
        assert main(["no"]) == 1
        os.write(fd, b"after")
    finally:
        os.close(fd)
    assert target.read_bytes() == b""


def test_a_closed_pipe_without_a_descriptor_is_still_quiet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class NoDescriptor(ClosedPipe):
        def fileno(self) -> int:
            raise io.UnsupportedOperation("fileno")

    monkeypatch.setattr(sys, "stdout", NoDescriptor(-1))
    assert main(["off"]) == 1
