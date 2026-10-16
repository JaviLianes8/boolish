"""Check the vocabularies against real parsers and the specifications they follow.

``fixtures/oracles.json`` holds what seven real parsers answered on a hand-written corpus
(``scripts/capture_oracles.py``: the stdlib ``distutils.util.strtobool`` of Python 3.11,
setuptools' copy, python-strtobool, ``configparser``, click, PyYAML for YAML 1.1 and
ruamel.yaml for YAML 1.2). ``configparser`` and, below Python 3.12, ``distutils`` are also
asked live. The fetched specifications live in ``sources/`` (see its manifest).
"""

from __future__ import annotations

import configparser
import json
import sys
import warnings
from pathlib import Path

import pytest

from boolish import CLASSIC, DEFAULT, MULTILINGUAL, BoolRules, strtobool

HERE = Path(__file__).resolve().parent
ORACLES = json.loads((HERE / "fixtures" / "oracles.json").read_text("utf-8"))["tools"]
CORPUS = list(ORACLES["distutils"]["results"])
STDLIB_FAMILY = ["distutils", "setuptools", "python-strtobool"]


def answer(text: str, rules: BoolRules) -> bool | None:
    return strtobool(text, None, rules=rules)


@pytest.mark.parametrize("tool", STDLIB_FAMILY)
def test_classic_is_the_stdlib_function_plus_surrounding_space(tool: str) -> None:
    results = ORACLES[tool]["results"]
    for text in CORPUS:
        assert answer(text, CLASSIC) == results.get(text.strip()), (tool, text)


@pytest.mark.parametrize("tool", STDLIB_FAMILY)
def test_the_stdlib_family_only_differs_on_surrounding_space(tool: str) -> None:
    for text, expected in ORACLES[tool]["results"].items():
        if text == text.strip():
            assert answer(text, CLASSIC) == expected, (tool, text)
            assert answer(text, DEFAULT) == expected or expected is None, (tool, text)


@pytest.mark.parametrize("tool", sorted(ORACLES))
@pytest.mark.parametrize("rules", [CLASSIC, DEFAULT, MULTILINGUAL], ids=["c", "d", "m"])
def test_no_vocabulary_ever_contradicts_a_real_parser(tool: str, rules: BoolRules) -> None:
    for text, expected in ORACLES[tool]["results"].items():
        ours = answer(text, rules)
        if expected is not None and ours is not None:
            assert ours == expected, (tool, text)


def test_default_accepts_everything_the_real_parsers_accept_but_blank_click_input() -> None:
    refused = {
        (tool, text)
        for tool, data in ORACLES.items()
        for text, expected in data["results"].items()
        if expected is not None and answer(text, DEFAULT) is None
    }
    # click 8.5 reads an empty or blank value as False; boolish refuses it on purpose.
    assert refused == {("click", text) for text in ["", " ", "\n", "\t "]}


def test_configparser_live_agrees_with_default() -> None:
    states = configparser.RawConfigParser.BOOLEAN_STATES
    assert set(states) <= DEFAULT.true | DEFAULT.false
    for word, value in states.items():
        assert strtobool(word) is value
        assert strtobool(word.upper()) is value


@pytest.mark.skipif(sys.version_info >= (3, 12), reason="distutils was removed in 3.12")
def test_distutils_live_agrees_with_classic() -> None:  # pragma: no cover - 3.10, 3.11
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from distutils.util import strtobool as stdlib_strtobool
    for text in CORPUS:
        try:
            expected: bool | None = bool(stdlib_strtobool(text.strip()))
        except ValueError:
            expected = None
        assert answer(text, CLASSIC) == expected, text


def source(name: str) -> str:
    path = HERE / "sources" / name
    if not path.is_file():
        pytest.skip(f"{name} not fetched (run scripts/fetch_sources.py)")
    return path.read_text("utf-8")


def test_classic_is_exactly_the_tuples_in_cpython_3_11() -> None:
    import ast

    tree = ast.parse(source("distutils-util-3.11.py.txt"))
    func = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "strtobool"
    )
    tuples = [node for node in ast.walk(func) if isinstance(node, ast.Tuple)]
    true, false = (frozenset(ast.literal_eval(item) for item in node.elts) for node in tuples[:2])
    assert (CLASSIC.true, CLASSIC.false) == (true, false)


def test_yaml_1_1_boolean_words_all_parse_with_their_meaning() -> None:
    page = source("yaml-1.1-bool.html")
    start = page.index("y|Y|yes")
    words = "".join(page[start : page.index("Definition", start)].split()).split("<")[0]
    found = {word.lower() for word in words.split("|")}
    assert found == {"y", "yes", "n", "no", "true", "false", "on", "off"}
    for word in words.split("|"):
        assert strtobool(word) is (word.lower() in {"y", "yes", "true", "on"}), word


def test_yaml_1_2_core_schema_booleans_parse() -> None:
    page = source("yaml-1.2.2.html")
    assert "true | True | TRUE | false | False | FALSE" in page
    for word in ["true", "True", "TRUE"]:
        assert strtobool(word, rules=CLASSIC) is True
    for word in ["false", "False", "FALSE"]:
        assert strtobool(word, rules=CLASSIC) is False


LANGS = ["en", "es", "fr", "de", "it", "pt"]


@pytest.mark.parametrize("lang", LANGS)
def test_cldr_yes_and_no_words_parse_leniently(lang: str) -> None:
    data = json.loads(source(f"cldr-posix-{lang}.json"))
    messages = data["main"][lang]["posix"]["messages"]
    for key, meaning in (("yesstr", True), ("nostr", False)):
        for word in messages[key].split(":"):
            if len(word) > 1 or word in {"y", "n"}:
                assert strtobool(word, rules=MULTILINGUAL, strict=False) is meaning, word


def test_cldr_one_letter_answers_outside_english_are_not_words() -> None:
    letters = set()
    for lang in LANGS:
        data = json.loads(source(f"cldr-posix-{lang}.json"))
        for text in data["main"][lang]["posix"]["messages"].values():
            letters |= {word for word in text.split(":") if len(word) == 1}
    unknown = {letter for letter in letters if strtobool(letter, None, rules=MULTILINGUAL) is None}
    assert unknown == {"s", "o", "j"}


def test_pep_632_dates_the_deprecation_and_the_removal() -> None:
    text = " ".join(source("pep-0632.html").split())
    assert "In Python 3.10 and 3.11, distutils will be formally marked as deprecated" in text
    assert "no longer work from Python 3.12" in text
