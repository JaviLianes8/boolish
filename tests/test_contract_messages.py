"""Contracts on the exact text of three error messages, added in 1.0.1.

A float is shown by the value it holds, through the plain float ``repr``. The name of an
environment variable is shown like any other text: by its plain characters, cut to the
first 32. The words a vocabulary refuses are listed sorted.
"""

from __future__ import annotations

import pytest

from boolish import BoolishError, BoolRules, NotBooleanError, getenv_bool, to_bool
from boolish._cli import main


class ShiftyFloat(float):
    """A float that would describe and convert itself differently if it were asked."""

    def __repr__(self) -> str:
        return "shifty repr"

    def __str__(self) -> str:
        return "shifty str"

    def __format__(self, spec: str) -> str:
        return "shifty format"

    def __float__(self) -> float:
        return 9.0


class ShiftyName(str):
    """A variable name whose own ``repr`` would print something else."""

    def __repr__(self) -> str:
        return "shifty name"


@pytest.mark.parametrize(
    ("value", "shown"),
    [
        (2.5, "2.5"),
        (-0.5, "-0.5"),
        (0.1, "0.1"),
        (1e300, "1e+300"),
        (float("nan"), "nan"),
        (float("-inf"), "-inf"),
        (ShiftyFloat(2.5), "2.5"),
        (ShiftyFloat(float("inf")), "inf"),
    ],
    ids=["plain", "negative", "shortest", "exponent", "nan", "infinity", "sub", "sub-inf"],
)
def test_a_float_is_shown_by_the_plain_repr_of_the_value_it_holds(value: float, shown: str) -> None:
    with pytest.raises(NotBooleanError) as info:
        to_bool(value)
    assert info.value.value is value
    assert str(info.value) == f"{shown} is not a recognised boolean"


@pytest.mark.parametrize(
    ("name", "shown"),
    [
        ("B" * 32, "'" + "B" * 32 + "'"),
        ("B" * 33, "'" + "B" * 32 + "'..."),
        ("BOOLISH_" + "X" * 100, "'BOOLISH_" + "X" * 24 + "'..."),
    ],
    ids=["32", "33", "108"],
)
def test_the_variable_name_is_cut_to_its_first_32_characters(
    monkeypatch: pytest.MonkeyPatch, name: str, shown: str
) -> None:
    monkeypatch.setenv(name, "maybe")
    with pytest.raises(NotBooleanError) as info:
        getenv_bool(name)
    assert info.value.variable == name
    assert str(info.value) == (
        f"environment variable {shown}: a value of 5 characters is not a recognised boolean"
    )


def test_the_variable_name_is_shown_by_its_plain_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHIFTY", "maybe")
    with pytest.raises(NotBooleanError) as info:
        getenv_bool(ShiftyName("SHIFTY"))
    assert str(info.value) == (
        "environment variable 'SHIFTY': a value of 5 characters is not a recognised boolean"
    )


def _refusal(true: list[str], false: list[str]) -> str:
    with pytest.raises(BoolishError) as info:
        BoolRules(true=true, false=false)
    return str(info.value)


def _quoted(letters: str) -> str:
    return ", ".join(f"'{letter}'" for letter in letters)


def test_words_on_both_sides_are_listed_sorted() -> None:
    words = list("jihgfedcba")
    expected = "words marked both true and false: " + _quoted("abcdefghij")
    assert _refusal(words, words) == expected


def test_words_that_collide_once_folded_are_listed_sorted() -> None:
    expected = "words collide once accents are folded: " + _quoted("aceinosuyz")
    assert _refusal(list("žýúšóñíéçá"), list("zyusonieca")) == expected


def test_the_command_prints_the_sorted_listing(capsys: pytest.CaptureFixture[str]) -> None:
    argv: list[str] = []
    for word in "kjihgedcba":
        argv += ["--true", word, "--false", word]
    assert main([*argv, "x"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"boolish: words marked both true and false: {_quoted('abcdeghijk')}\n"
