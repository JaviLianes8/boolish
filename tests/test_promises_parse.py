"""The 1.0.0 promises of strtobool, to_bool and the two predicates."""

from __future__ import annotations

import enum
import math

import pytest

from boolish import (
    CLASSIC,
    DEFAULT,
    MULTILINGUAL,
    NotBooleanError,
    is_falsy,
    is_truthy,
    strtobool,
    to_bool,
)


class Lying(str):
    def strip(self, chars: str | None = None) -> str:
        return "yes"

    def lower(self) -> str:
        return "yes"


class LyingInt(int):
    def __eq__(self, other: object) -> bool:
        return True

    __hash__ = int.__hash__


class Level(enum.IntEnum):
    OFF = 0
    ON = 1
    HIGH = 2


@pytest.mark.parametrize("value", [1, 1.5, b"yes", bytearray(b"1"), None, ["yes"]])
def test_strtobool_refuses_non_strings_with_type_error(value: object) -> None:
    with pytest.raises(TypeError, match="strtobool expects a str, not "):
        strtobool(value)  # type: ignore[call-overload]
    with pytest.raises(TypeError):
        strtobool(value, False)  # type: ignore[call-overload]


@pytest.mark.parametrize("text", [" yes", "yes\n", "\tYES\r\n", "\u00a0on\u3000", "\x0bTrue\x0c"])
def test_any_surrounding_whitespace_is_ignored(text: str) -> None:
    assert strtobool(text) is True


@pytest.mark.parametrize("text", ["", "   ", "y e s", "yes!", "ye", "yess", "2", "-1", "1.0", "00"])
def test_near_misses_are_refused(text: str) -> None:
    with pytest.raises(NotBooleanError):
        strtobool(text)


def test_the_default_comes_back_as_the_same_object() -> None:
    marker = object()
    assert strtobool("maybe", marker) is marker
    assert to_bool("maybe", marker) is marker
    assert strtobool("maybe", None) is None
    assert strtobool("yes", marker) is True


def test_rules_and_strict_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        strtobool("yes", None, DEFAULT)  # type: ignore[call-overload]
    with pytest.raises(TypeError):
        to_bool("yes", None, DEFAULT)  # type: ignore[call-overload]


def test_a_str_subclass_cannot_override_the_matching() -> None:
    assert strtobool(Lying("no")) is False
    assert strtobool(Lying("No"), strict=False) is False


def test_lenient_folds_compatibility_forms_and_marks() -> None:
    fullwidth = "".join(chr(0xFF00 + ord(ch) - 0x20) for ch in "YES")
    assert strtobool(fullwidth, strict=False) is True
    assert strtobool("N\u0303O", strict=False) is False
    assert strtobool("NA\u0303O", rules=MULTILINGUAL, strict=False) is False
    with pytest.raises(NotBooleanError):
        strtobool(fullwidth)


def test_lenient_matches_accented_vocabulary_against_plain_input() -> None:
    spanish = CLASSIC.extend(true={"sí"}, false={"falso"})
    assert strtobool("SI", rules=spanish, strict=False) is True
    assert strtobool("sí", rules=spanish) is True
    with pytest.raises(NotBooleanError):
        strtobool("si", rules=spanish)


def test_classic_refuses_the_default_extras() -> None:
    for word in ("enable", "enabled", "disable", "disabled"):
        assert strtobool(word, None, rules=CLASSIC) is None
        assert isinstance(strtobool(word), bool)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, True), (False, False), (1, True), (0, False), (1.0, True), (0.0, False), (-0.0, False)],
)
def test_to_bool_numbers_and_booleans(value: object, expected: bool) -> None:
    assert to_bool(value) is expected  # type: ignore[call-overload]
    assert to_bool(value, strict=False) is expected  # type: ignore[call-overload]


@pytest.mark.parametrize("value", [2, -1, 0.5, 10**30, -(10**400)])
def test_other_finite_numbers_are_true_only_when_lenient(value: int | float) -> None:
    with pytest.raises(NotBooleanError):
        to_bool(value)
    assert to_bool(value, strict=False) is True
    assert is_truthy(value) is False
    assert is_truthy(value, strict=False) is True


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nan_and_infinity_are_never_boolean(value: float) -> None:
    for strict in (True, False):
        with pytest.raises(NotBooleanError):
            to_bool(value, strict=strict)
        assert to_bool(value, None, strict=strict) is None


def test_number_subclasses_are_read_by_value() -> None:
    assert to_bool(LyingInt(5), None) is None
    assert to_bool(Level.ON) is True
    assert to_bool(Level.OFF) is False
    assert to_bool(Level.HIGH, strict=False) is True


@pytest.mark.parametrize("value", [None, [1], (), {}, b"1", object(), 1j])
def test_other_types_raise_not_boolean_or_give_the_default(value: object) -> None:
    with pytest.raises(NotBooleanError):
        to_bool(value)  # type: ignore[call-overload]
    assert to_bool(value, "d") == "d"  # type: ignore[call-overload]
    assert is_truthy(value) is False  # type: ignore[arg-type]
    assert is_falsy(value) is False  # type: ignore[arg-type]


def test_to_bool_reads_strings_like_strtobool() -> None:
    assert to_bool(" Off ") is False
    assert to_bool("oui", rules=MULTILINGUAL) is True
    assert to_bool("Sí", rules=MULTILINGUAL, strict=False) is True
    with pytest.raises(NotBooleanError):
        to_bool("Sí", rules=MULTILINGUAL)


@pytest.mark.parametrize("value", ["yes", "no", "maybe", 0, 1, 2, None, 0.5, True, False])
def test_predicates_are_mirrors_never_both_true(value: object) -> None:
    truthy, falsy = is_truthy(value), is_falsy(value)  # type: ignore[arg-type]
    assert not (truthy and falsy)
    result = to_bool(value, None)  # type: ignore[call-overload]
    assert truthy is (result is True)
    assert falsy is (result is False)


def test_predicates_honour_rules_and_strict() -> None:
    assert is_truthy("ja", rules=MULTILINGUAL) is True
    assert is_falsy("NÃO", rules=MULTILINGUAL, strict=False) is True
    assert is_falsy("NÃO", rules=MULTILINGUAL) is False
    assert is_truthy("enable", rules=CLASSIC) is False
