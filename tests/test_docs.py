"""Every example in the docstrings, README and GUIDE runs and prints what it shows."""

from __future__ import annotations

import doctest
import importlib
import os
import re
import shlex
from collections.abc import Iterator
from pathlib import Path

import pytest

import boolish
from boolish._cli import main

ROOT = Path(__file__).resolve().parent.parent
MODULES = [
    "boolish",
    "boolish._cli",
    "boolish._coerce",
    "boolish._env",
    "boolish._errors",
    "boolish._normalize",
    "boolish._parse",
    "boolish._rules",
]
DOCS = ["README.md", "GUIDE.md"]
FLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
LONG_DASH = chr(0x2014)


def _blocks(name: str, language: str) -> list[str]:
    text = (ROOT / name).read_text("utf-8")
    return re.findall("```" + language + "\n(.*?)```", text, flags=re.S)


@pytest.fixture
def clean_environ() -> Iterator[None]:
    saved = dict(os.environ)
    yield None
    os.environ.clear()
    os.environ.update(saved)


@pytest.mark.parametrize("name", MODULES)
def test_module_doctests_pass(name: str, clean_environ: None) -> None:
    result = doctest.testmod(importlib.import_module(name), optionflags=FLAGS)
    assert result.failed == 0


def test_every_public_name_has_a_runnable_example() -> None:
    lines = (boolish.__doc__ or "").splitlines()
    examples = " ".join(line for line in lines if line.startswith(">>> "))
    words = set(re.findall("[A-Za-z_]+", examples))
    for name in boolish.__all__:
        obj = getattr(boolish, name)
        if name != "BoolLike" and (isinstance(obj, type) or callable(obj)):
            assert ">>> " in (obj.__doc__ or ""), name
        else:
            assert name in words, name


@pytest.mark.parametrize("name", DOCS)
def test_pycon_examples_run_and_print_what_they_show(name: str, clean_environ: None) -> None:
    blocks = _blocks(name, "pycon")
    assert blocks
    parser = doctest.DocTestParser()
    runner = doctest.DocTestRunner(optionflags=FLAGS)
    globs: dict[str, object] = {}
    for number, block in enumerate(blocks):
        test = parser.get_doctest(block, globs, f"{name}[{number}]", name, 0)
        runner.run(test, clear_globs=False)
        globs = test.globs
    assert runner.summarize(verbose=False).failed == 0


@pytest.mark.parametrize("name", DOCS)
def test_console_transcripts_match_the_command(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    blocks = _blocks(name, "console")
    assert blocks
    for block in blocks:
        for command in re.split("^[$] ", block, flags=re.M)[1:]:
            line, _, expected = command.partition("\n")
            argv = shlex.split(line)
            assert argv[0] == "boolish"
            main(argv[1:])
            captured = capsys.readouterr()
            assert captured.out + captured.err == expected, line


def test_docs_link_absolutely_and_avoid_the_long_dash() -> None:
    for name in [*DOCS, "CHANGELOG.md", "CONTRIBUTING.md"]:
        text = (ROOT / name).read_text("utf-8")
        assert LONG_DASH not in text, name
        for target in re.findall("[]][(]([^)]+)[)]", text):
            assert target.startswith("https://"), (name, target)
