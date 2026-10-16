"""Hostile input: lying subclasses, mocks, odd type names, closed streams, odd consoles."""

from __future__ import annotations

import io
import random
import sys
import time
from unittest import mock

import pytest

from boolish import (
    DEFAULT,
    MULTILINGUAL,
    BoolRules,
    NotBooleanError,
    getenv_bool,
    is_falsy,
    is_truthy,
    strtobool,
    to_bool,
)
from boolish._cli import main
from boolish._normalize import fold, fold_within

WIDE = chr(0xFDFA)  # one character that decomposes into eighteen, fifteen of them not spaces


class LenRaises(str):
    def __len__(self) -> int:
        raise RuntimeError("len")


class GetItemLies(str):
    def __getitem__(self, key: object) -> str:
        raise TypeError("getitem")

    def isascii(self) -> bool:
        return True


class BitLengthRaises(int):
    def bit_length(self) -> int:
        raise RuntimeError("bit_length")


@pytest.mark.parametrize("cls", [LenRaises, GetItemLies])
def test_str_subclasses_are_read_as_plain_text(cls: type[str]) -> None:
    for strict in (True, False):
        assert strtobool(cls(" Yes "), strict=strict) is True
        assert is_truthy(cls("S\u00ed"), rules=MULTILINGUAL, strict=False) is True
        with pytest.raises(NotBooleanError) as info:
            strtobool(cls("banana"), strict=strict)
        assert str(info.value) == "'banana' is not a recognised boolean"


def test_int_subclasses_cannot_break_the_message() -> None:
    with pytest.raises(NotBooleanError, match=r"^5 is not a recognised boolean$"):
        to_bool(BitLengthRaises(5))
    assert to_bool(BitLengthRaises(1)) is True


@pytest.mark.parametrize("spec", [bool, str, int, float])
def test_mocks_that_fake_their_class_are_not_boolean(spec: type) -> None:
    fake = mock.Mock(spec=spec)
    assert isinstance(fake, spec)
    assert is_truthy(fake) is False
    assert is_falsy(fake) is False
    assert to_bool(fake, "default") == "default"
    with pytest.raises(NotBooleanError, match="a value of type Mock is not"):
        to_bool(fake)


def test_type_names_are_escaped_in_messages() -> None:
    evil = type("\x1b[2J\x07\n", (), {})()
    for call in (lambda: to_bool(evil), lambda: strtobool(evil), lambda: BoolRules([evil])):
        with pytest.raises((NotBooleanError, TypeError)) as info:
            call()
        assert str(info.value).isprintable()
        assert "\\x1b[2J\\x07\\n" in str(info.value)


def test_lenient_matching_stops_early_on_expanding_input() -> None:
    start = time.perf_counter()
    assert is_truthy(WIDE * 10**6, strict=False) is False
    assert time.perf_counter() - start < 0.5
    assert fold_within(WIDE, 14) is None
    assert fold_within(WIDE, 15) == fold(WIDE)


def test_bounded_folding_equals_folding_when_it_does_not_stop() -> None:
    rng = random.Random(7)
    pieces = ["Y", "e", "S", " ", "\u00a8", "\u0301", WIDE, "\uff59", "\u0130", "\u00a0"]
    for _ in range(3000):
        text = "".join(rng.choices(pieces, k=rng.randint(0, 12)))
        full = fold(text)
        non_space = sum(1 for ch in full if not ch.isspace())
        assert fold_within(text, max(non_space, 0) + 50) == full
        if non_space:
            assert fold_within(text, non_space - 1) is None


def test_an_empty_word_cannot_be_matched_by_overlong_input() -> None:
    rules = DEFAULT.extend(false={""})
    assert strtobool("", rules=rules) is False
    assert strtobool(WIDE * 5000, None, rules=rules, strict=False) is None


def test_closed_standard_streams_keep_the_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdout", None)
    assert main(["yes"]) == 0
    assert main(["no"]) == 1
    monkeypatch.setattr(sys, "stderr", None)
    assert main(["banana"]) == 2
    with pytest.raises(SystemExit) as exc:
        main(["yes", "extra"])
    assert exc.value.code == 2


def test_usage_errors_escape_and_bound_the_argument(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["yes", "\x1b]0;x\x07" + "z" * 30_000])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "\x1b" not in err
    assert "\\x1b]0;x\\x07" in err
    assert len(err) < 800


@pytest.mark.parametrize("encoding", ["ascii", "cp932", "cp1252"])
def test_help_survives_any_console_encoding(monkeypatch: pytest.MonkeyPatch, encoding: str) -> None:
    stream = io.TextIOWrapper(io.BytesIO(), encoding=encoding, newline="\n")
    monkeypatch.setattr(sys, "stdout", stream)
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    stream.flush()
    assert b"examples:" in stream.buffer.getvalue()


def test_environment_errors_chain_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOOLISH_SECRET", "sk_live_" + "A" * 40)
    with pytest.raises(NotBooleanError) as info:
        getenv_bool("BOOLISH_SECRET")
    assert info.value.__context__ is None
    assert info.value.__cause__ is None
    assert "sk_live" not in str(info.value)


class _NameLies(type):
    @property
    def __name__(cls) -> str:  # type: ignore[override]
        raise KeyError("name")


class Disguised(metaclass=_NameLies):
    pass


def test_a_metaclass_cannot_break_the_type_name() -> None:
    with pytest.raises(NotBooleanError, match="a value of type Disguised is not"):
        to_bool(Disguised())  # type: ignore[call-overload]
    with pytest.raises(TypeError, match="not Disguised"):
        strtobool(Disguised())  # type: ignore[call-overload]
