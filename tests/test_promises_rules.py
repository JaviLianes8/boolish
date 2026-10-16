"""The 1.0.0 promises of BoolRules, the errors and getenv_bool."""

from __future__ import annotations

import copy
import dataclasses
import pickle

import pytest

from boolish import (
    CLASSIC,
    DEFAULT,
    MULTILINGUAL,
    BoolishError,
    BoolRules,
    NotBooleanError,
    getenv_bool,
    strtobool,
)


def test_words_are_trimmed_and_lower_cased() -> None:
    rules = BoolRules(true=[" Aye ", "YES"], false=("\tNay",))
    assert rules.true == {"aye", "yes"}
    assert rules.false == {"nay"}
    assert isinstance(rules.true, frozenset)


def test_positional_construction_and_generators_work() -> None:
    rules = BoolRules((w for w in ["up"]), iter(["down"]))
    assert rules.true == {"up"}
    assert rules.false == {"down"}


@pytest.mark.parametrize("bad", ["yes", b"yes", bytearray(b"yes")])
def test_a_bare_string_is_refused_everywhere(bad: object) -> None:
    with pytest.raises(TypeError, match="true must be a collection of words, not a single"):
        BoolRules(true=bad)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="false must be a collection of words"):
        BoolRules(false=bad)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="true must be a collection"):
        DEFAULT.extend(true=bad)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="false must be a collection"):
        DEFAULT.extend(false=bad)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [1, None, b"x"])
def test_a_word_that_is_not_a_string_is_refused(bad: object) -> None:
    with pytest.raises(TypeError, match="true words must be str, not "):
        BoolRules(true=["yes", bad])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="false words must be str"):
        DEFAULT.extend(false=[bad])  # type: ignore[list-item]


def test_overlap_and_folded_collisions_raise_boolish_error() -> None:
    with pytest.raises(BoolishError, match=r"^words marked both true and false: 'on'$"):
        BoolRules(true={"yes", "On "}, false={"on", "no"})
    with pytest.raises(BoolishError, match=r"^words collide once accents are folded: 'si'$"):
        BoolRules(true={"sí"}, false={"si"})
    with pytest.raises(BoolishError, match="both true and false: 'no'"):
        DEFAULT.extend(true={"no"})


def test_clash_messages_stay_short() -> None:
    words = {f"{n:03d}" + "x" * 5000 for n in range(50)}
    with pytest.raises(BoolishError) as info:
        BoolRules(true=words, false=words)
    message = str(info.value)
    assert len(message) < 600
    assert message.endswith(", ...")
    assert message.count("'...") == 10


def test_rulesets_are_frozen_comparable_and_hashable() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT.true = frozenset()  # type: ignore[misc]
    assert BoolRules(["a"], ["b"]) == BoolRules({"A"}, {" b"})
    assert BoolRules(["a"], ["b"]) != BoolRules(["b"], ["a"])
    assert hash(BoolRules(["a"], ["b"])) == hash(BoolRules(["A"], ["B"]))
    assert len({CLASSIC, BoolRules(), DEFAULT}) == 2


def test_repr_is_sorted_and_round_trips() -> None:
    assert repr(CLASSIC) == (
        "BoolRules(true=['1', 'on', 't', 'true', 'y', 'yes'], "
        "false=['0', 'f', 'false', 'n', 'no', 'off'])"
    )
    assert eval(repr(MULTILINGUAL), {"BoolRules": BoolRules}) == MULTILINGUAL


def test_pickle_copy_and_replace_keep_lenient_matching() -> None:
    for clone in (
        pickle.loads(pickle.dumps(MULTILINGUAL)),
        copy.deepcopy(MULTILINGUAL),
        dataclasses.replace(MULTILINGUAL),
    ):
        assert clone == MULTILINGUAL
        assert strtobool("NÃO", rules=clone, strict=False) is False
    swapped = dataclasses.replace(CLASSIC, true=frozenset({"sí"}))
    assert strtobool("SI", rules=swapped, strict=False) is True


def test_extend_leaves_the_original_untouched() -> None:
    before = (DEFAULT.true, DEFAULT.false)
    bigger = DEFAULT.extend(true={" Aye"})
    assert (DEFAULT.true, DEFAULT.false) == before
    assert bigger.true == DEFAULT.true | {"aye"}
    assert bigger.false == DEFAULT.false
    assert DEFAULT.extend() == DEFAULT


def test_not_boolean_error_message_value_and_variable() -> None:
    error = NotBooleanError("banana")
    assert str(error) == "'banana' is not a recognised boolean"
    assert (error.value, error.variable) == ("banana", None)
    assert isinstance(error, BoolishError)
    assert isinstance(error, ValueError)


@pytest.mark.parametrize(
    ("value", "shown"),
    [
        ("x" * 32, "'" + "x" * 32 + "'"),
        ("x" * 33, "'" + "x" * 32 + "'..."),
        ("a\x00\u202e", "'a\\x00\\u202e'"),
        (None, "None"),
        (False, "False"),
        (-(2**64) + 1, str(-(2**64) + 1)),
        (2**64, "an int of 65 bits"),
        (1.5, "1.5"),
        ([1] * 10**5, "a value of type list"),
        (type("N" * 60, (), {})(), "a value of type " + "N" * 40),
    ],
)
def test_messages_show_a_bounded_preview(value: object, shown: str) -> None:
    assert str(NotBooleanError(value)) == f"{shown} is not a recognised boolean"


def test_a_huge_input_never_reaches_the_message() -> None:
    with pytest.raises(NotBooleanError) as info:
        strtobool("s" * 10**6)
    assert len(str(info.value)) < 80
    assert info.value.value == "s" * 10**6


def test_errors_survive_pickling() -> None:
    error = NotBooleanError("banana", variable="FLAG")
    clone = pickle.loads(pickle.dumps(error))
    assert type(clone) is NotBooleanError
    assert (clone.value, clone.variable, str(clone)) == ("banana", "FLAG", str(error))


def test_getenv_bool_unset_set_and_bad(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOOLISH_FLAG", raising=False)
    assert getenv_bool("BOOLISH_FLAG") is None
    marker = object()
    assert getenv_bool("BOOLISH_FLAG", marker) is marker
    monkeypatch.setenv("BOOLISH_FLAG", " Disabled ")
    assert getenv_bool("BOOLISH_FLAG", True) is False
    assert getenv_bool("BOOLISH_FLAG", rules=DEFAULT, strict=True) is False
    monkeypatch.setenv("BOOLISH_FLAG", "")
    with pytest.raises(NotBooleanError) as info:
        getenv_bool("BOOLISH_FLAG", False)
    assert info.value.variable == "BOOLISH_FLAG"
    assert info.value.value == ""
    assert str(info.value) == (
        "environment variable 'BOOLISH_FLAG': a value of 0 characters is not a recognised boolean"
    )


def test_getenv_bool_passes_rules_and_strict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOOLISH_FLAG", "enabled")
    with pytest.raises(NotBooleanError):
        getenv_bool("BOOLISH_FLAG", rules=CLASSIC)
    monkeypatch.setenv("BOOLISH_FLAG", "Sí")
    with pytest.raises(NotBooleanError):
        getenv_bool("BOOLISH_FLAG", rules=MULTILINGUAL)
    assert getenv_bool("BOOLISH_FLAG", rules=MULTILINGUAL, strict=False) is True
