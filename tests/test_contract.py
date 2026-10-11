"""The complete promise of every public name. This file is the contract."""

import importlib.resources

import pytest

import boolish
from boolish import (
    DEFAULT,
    MULTILINGUAL,
    BoolishError,
    BoolRules,
    NotBooleanError,
    getenv_bool,
    is_falsy,
    is_truthy,
    strtobool,
    to_bool,
)

PUBLIC_API = [
    "BoolLike",
    "BoolRules",
    "BoolishError",
    "DEFAULT",
    "MULTILINGUAL",
    "NotBooleanError",
    "getenv_bool",
    "is_falsy",
    "is_truthy",
    "strtobool",
    "to_bool",
]

DEFAULT_TRUE = ["y", "yes", "t", "true", "on", "1", "enable", "enabled"]
DEFAULT_FALSE = ["n", "no", "f", "false", "off", "0", "disable", "disabled"]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(boolish.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in boolish.__all__:
        assert hasattr(boolish, name)


def test_version_is_a_three_part_string() -> None:
    parts = boolish.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("boolish").joinpath("py.typed").is_file()


@pytest.mark.parametrize("word", DEFAULT_TRUE)
def test_default_truthy_vocabulary(word: str) -> None:
    assert strtobool(word) is True
    assert to_bool(word) is True
    assert is_truthy(word) is True


@pytest.mark.parametrize("word", DEFAULT_FALSE)
def test_default_falsy_vocabulary(word: str) -> None:
    assert strtobool(word) is False
    assert to_bool(word) is False
    assert is_falsy(word) is True


def test_strtobool_ignores_case_and_surrounding_space() -> None:
    assert strtobool("  YES ") is True
    assert strtobool("Off") is False


def test_strtobool_raises_a_typed_error_without_a_default() -> None:
    with pytest.raises(NotBooleanError):
        strtobool("maybe")
    assert issubclass(NotBooleanError, BoolishError)
    assert issubclass(BoolishError, ValueError)


def test_strtobool_returns_the_default_when_given() -> None:
    assert strtobool("maybe", None) is None
    assert strtobool("maybe", "skip") == "skip"


def test_strtobool_result_is_a_real_bool() -> None:
    assert isinstance(strtobool("yes"), bool)


def test_strict_mode_rejects_accented_input() -> None:
    with pytest.raises(NotBooleanError):
        strtobool("Sí", rules=MULTILINGUAL)


def test_lenient_mode_folds_accents() -> None:
    assert strtobool("Sí", rules=MULTILINGUAL, strict=False) is True
    assert strtobool("si", rules=MULTILINGUAL, strict=False) is True


def test_to_bool_accepts_booleans() -> None:
    assert to_bool(True) is True
    assert to_bool(False) is False


@pytest.mark.parametrize(("value", "expected"), [(1, True), (0, False), (1.0, True), (0.0, False)])
def test_to_bool_accepts_zero_and_one(value: object, expected: bool) -> None:
    assert to_bool(value) is expected  # type: ignore[arg-type]


def test_to_bool_strict_rejects_other_numbers() -> None:
    with pytest.raises(NotBooleanError):
        to_bool(5)
    with pytest.raises(NotBooleanError):
        to_bool(2.5)


def test_to_bool_lenient_treats_nonzero_as_true() -> None:
    assert to_bool(5, strict=False) is True
    assert to_bool(-0.1, strict=False) is True
    assert to_bool(0, strict=False) is False


def test_to_bool_handles_none() -> None:
    assert to_bool(None, False) is False
    with pytest.raises(NotBooleanError):
        to_bool(None)


def test_to_bool_rejects_unknown_types() -> None:
    with pytest.raises(NotBooleanError):
        to_bool([1, 2], rules=DEFAULT)  # type: ignore[arg-type]


def test_predicates_never_raise_on_unknown_input() -> None:
    assert is_truthy("maybe") is False
    assert is_falsy("maybe") is False
    assert is_truthy(None) is False
    assert is_falsy(None) is False
    assert is_truthy(object()) is False  # type: ignore[arg-type]


def test_is_truthy_and_is_falsy_are_not_mere_negations() -> None:
    assert is_truthy("maybe") is False
    assert is_falsy("maybe") is False


def test_boolrules_rejects_overlap() -> None:
    with pytest.raises(BoolishError):
        BoolRules(true={"yes", "on"}, false={"on", "no"})


def test_boolrules_rejects_accent_collision() -> None:
    with pytest.raises(BoolishError):
        BoolRules(true={"sí"}, false={"si"})


def test_boolrules_extend_adds_words_without_mutating() -> None:
    extended = DEFAULT.extend(true={"aye"}, false={"nay"})
    assert strtobool("aye", rules=extended) is True
    assert strtobool("nay", rules=extended) is False
    assert strtobool("yes", rules=extended) is True
    with pytest.raises(NotBooleanError):
        strtobool("aye", rules=DEFAULT)


@pytest.mark.parametrize("word", ["oui", "ja", "sim", "verdadero", "vero", "wahr"])
def test_multilingual_truthy_forms(word: str) -> None:
    assert strtobool(word, rules=MULTILINGUAL) is True


@pytest.mark.parametrize("word", ["non", "nein", "nao", "falso", "faux", "falsch"])
def test_multilingual_falsy_forms(word: str) -> None:
    assert strtobool(word, rules=MULTILINGUAL) is False


def test_getenv_bool_reads_parses_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEATURE_X", "true")
    assert getenv_bool("FEATURE_X") is True
    monkeypatch.delenv("FEATURE_X", raising=False)
    assert getenv_bool("FEATURE_X") is None
    assert getenv_bool("FEATURE_X", False) is False


def test_getenv_bool_is_loud_on_a_bad_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEATURE_X", "banana")
    with pytest.raises(NotBooleanError):
        getenv_bool("FEATURE_X", False)


def test_getenv_bool_honours_lenient_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEATURE_X", "Sí")
    assert getenv_bool("FEATURE_X", False, rules=MULTILINGUAL, strict=False) is True
