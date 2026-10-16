"""Unit tests for the argparse command line interface."""

import pytest

from boolish._cli import main


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
