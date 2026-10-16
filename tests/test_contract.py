"""The public surface of boolish 1.0.0: names, signatures, vocabularies and metadata."""

from __future__ import annotations

import importlib.resources
import inspect
import sys
from pathlib import Path

import boolish
from boolish import CLASSIC, DEFAULT, MULTILINGUAL, BoolRules

PUBLIC_API = [
    "CLASSIC",
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

ROOT = Path(__file__).resolve().parent.parent


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(boolish.__all__) == sorted(PUBLIC_API)
    public = {name for name in vars(boolish) if not name.startswith("_")}
    assert public == set(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in boolish.__all__:
        assert hasattr(boolish, name)


def test_version_is_one_zero_zero_everywhere() -> None:
    assert boolish.__version__ == "1.0.0"
    if sys.version_info >= (3, 11):
        import tomllib

        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))
        assert pyproject["project"]["dynamic"] == ["version"]
        assert pyproject["tool"]["hatch"]["version"]["path"] == "src/boolish/_version.py"


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("boolish").joinpath("py.typed").is_file()


def test_public_classes_live_in_the_package_namespace() -> None:
    for cls in (boolish.BoolRules, boolish.BoolishError, boolish.NotBooleanError):
        assert cls.__module__ == "boolish"


P = inspect.Parameter
KW = P.KEYWORD_ONLY
POS = P.POSITIONAL_OR_KEYWORD


def _shape(func: object) -> list[tuple[str, object, str, object]]:
    params = inspect.signature(func).parameters.values()  # type: ignore[arg-type]
    return [(p.name, p.kind, p.annotation, p.default) for p in params]


def test_signatures_are_frozen() -> None:
    from boolish._parse import _MISSING

    tail = [("rules", KW, "BoolRules", DEFAULT), ("strict", KW, "bool", True)]
    assert _shape(boolish.strtobool) == [
        ("value", POS, "str", P.empty),
        ("default", POS, "object", _MISSING),
        *tail,
    ]
    assert _shape(boolish.to_bool) == [
        ("value", POS, "BoolLike", P.empty),
        ("default", POS, "object", _MISSING),
        *tail,
    ]
    assert _shape(boolish.getenv_bool) == [
        ("name", POS, "str", P.empty),
        ("default", POS, "object", None),
        *tail,
    ]
    for predicate in (boolish.is_truthy, boolish.is_falsy):
        assert _shape(predicate) == [("value", POS, "BoolLike", P.empty), *tail]
    assert _shape(BoolRules.extend) == [
        ("self", POS, P.empty, P.empty),
        ("true", KW, "Iterable[str]", ()),
        ("false", KW, "Iterable[str]", ()),
    ]
    assert [p.name for p in inspect.signature(BoolRules).parameters.values()] == [
        "true",
        "false",
    ]


def test_classic_is_the_removed_stdlib_vocabulary() -> None:
    assert BoolRules() == CLASSIC
    assert CLASSIC.true == {"y", "yes", "t", "true", "on", "1"}
    assert CLASSIC.false == {"n", "no", "f", "false", "off", "0"}


def test_default_adds_enable_and_disable() -> None:
    assert DEFAULT.true == CLASSIC.true | {"enable", "enabled"}
    assert DEFAULT.false == CLASSIC.false | {"disable", "disabled"}


def test_multilingual_vocabulary_is_pinned() -> None:
    extra_true = {"active", "ok", "si", "verdadero", "oui", "vrai", "ja", "wahr", "vero"}
    extra_true |= {"sim", "verdadeiro"}
    extra_false = {"inactive", "falso", "non", "faux", "nein", "falsch", "nao"}
    assert MULTILINGUAL.true == DEFAULT.true | extra_true
    assert MULTILINGUAL.false == DEFAULT.false | extra_false
    every = MULTILINGUAL.true | MULTILINGUAL.false
    assert all(word.isascii() for word in every)


def test_pyproject_metadata_for_a_stable_release() -> None:
    text = (ROOT / "pyproject.toml").read_text("utf-8")
    assert '"Development Status :: 5 - Production/Stable"' in text
    assert "dependencies = []" in text
    assert 'requires-python = ">=3.10"' in text
    for minor in range(10, 15):
        assert f'"Programming Language :: Python :: 3.{minor}"' in text
    for url in ("Homepage", "Source", "Issues", "Changelog"):
        assert f"\n{url} = " in text
