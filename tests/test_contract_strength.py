"""Contracts added after the blind mutation round: exact limits and defaults."""

from __future__ import annotations

import io
import sys

import pytest

from boolish import (
    DEFAULT,
    MULTILINGUAL,
    BoolishError,
    BoolRules,
    NotBooleanError,
    strtobool,
    to_bool,
)
from boolish._cli import main

ACUTE = chr(0x301)


class LyingFloat(float):
    def __eq__(self, other: object) -> bool:
        return True

    __hash__ = float.__hash__


@pytest.mark.parametrize("rules", [DEFAULT, MULTILINGUAL], ids=["default", "multilingual"])
def test_the_longest_word_still_matches_leniently_with_an_accent(rules: BoolRules) -> None:
    for side, meaning in ((rules.true, True), (rules.false, False)):
        longest = max(side, key=len)
        accented = longest[0] + ACUTE + longest[1:]
        assert strtobool(accented, rules=rules, strict=False) is meaning, longest


def test_a_float_subclass_is_read_by_its_value() -> None:
    assert to_bool(LyingFloat(7.0), None) is None
    assert to_bool(LyingFloat(1.0)) is True
    assert to_bool(LyingFloat(0.0)) is False


def test_an_environment_error_for_a_non_string_says_zero_characters() -> None:
    error = NotBooleanError(5, variable="X")
    assert (
        str(error)
        == "environment variable 'X': a value of 0 characters is not a recognised boolean"
    )


def _clash(count: int) -> str:
    words = [f"w{n:02d}" for n in range(count)]
    with pytest.raises(BoolishError) as info:
        BoolRules(true=words, false=words)
    return str(info.value)


def test_a_clash_lists_ten_words_and_marks_only_more() -> None:
    assert not _clash(10).endswith(", ...")
    assert _clash(10).count("'w") == 10
    assert _clash(11).endswith(", ...")
    assert _clash(11).count("'w") == 10


def test_the_command_uses_the_default_vocabulary(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["enabled"]) == 0
    assert main(["disabled"]) == 1
    assert capsys.readouterr().out == "true\nfalse\n"


def test_usage_errors_are_cut_at_exactly_300_characters(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from boolish._cli import _clean

    assert _clean("x" * 300) == "x" * 300
    assert _clean("x" * 301) == "x" * 300 + "..."
    with pytest.raises(SystemExit):
        main(["yes", "z" * 1000])
    last = capsys.readouterr().err.splitlines()[-1]
    assert last.startswith("boolish: error: ")
    assert last.endswith("z...")
    assert len(last) == len("boolish: error: ") + 300 + 3


def test_a_stream_without_an_encoding_gets_ascii(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stderr", stream)
    assert main(["S" + chr(0xED)]) == 2
    assert stream.getvalue() == "boolish: 'S\\xed' is not a recognised boolean\n"
