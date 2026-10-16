"""Record how real boolean parsers read a hand-written corpus of inputs.

Run it with a Python older than 3.12 (it still ships ``distutils``) inside a throwaway
virtual environment holding PyYAML, ruamel.yaml, click, setuptools and python-strtobool:

    SETUPTOOLS_USE_DISTUTILS=stdlib python scripts/capture_oracles.py tests/fixtures/oracles.json

(setuptools otherwise swaps its own copy in for ``distutils``; the script refuses that.)

Each tool is called as it is: nothing here reimplements a parser. The corpus is written
by hand (labelled as such in the output); the answers are the tools' own.
"""

from __future__ import annotations

import configparser
import datetime
import json
import platform
import sys
import warnings
from collections.abc import Callable
from importlib import metadata

WORDS = """
y yes t true on 1 n no f false off 0
enable enabled disable disabled active inactive ok okay
si sí oui non ja nein sim não nao vero falso vrai faux wahr falsch
verdadero verdadeiro none null ~ maybe yes! 2 -1 00 01 1.0 0.0 10
"""
# The empty string, a spaced word and full-width "yes".
BASE = [*WORDS.split(), "", "y e s", "\uff59\uff45\uff53"]


def corpus() -> list[str]:
    seen: dict[str, None] = {}
    for word in BASE:
        for form in (word, word.upper(), word.capitalize(), f" {word}", f"{word}\n", f"\t{word} "):
            seen[form] = None
    return list(seen)


def run(parse: Callable[[str], object]) -> dict[str, bool | None]:
    """Map each input to the tool's bool, or ``None`` when it refuses or gives a non-bool.

    ``distutils`` answers ``1``/``0``; those count as booleans. YAML integers do not.
    """
    results: dict[str, bool | None] = {}
    for text in corpus():
        try:
            value = parse(text)
        except Exception:
            results[text] = None
            continue
        results[text] = bool(value) if isinstance(value, bool) else None
    return results


def _as_bool(parse: Callable[[str], int]) -> Callable[[str], bool]:
    def call(text: str) -> bool:
        value = parse(text)
        if value not in (0, 1) or type(value) is not int:
            raise TypeError(f"unexpected answer {value!r}")
        return bool(value)

    return call


def _configparser(text: str) -> bool:
    parser = configparser.RawConfigParser()
    parser.read_dict({"section": {"key": text}})
    return parser.getboolean("section", "key")


def main() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import distutils.util

    if "site-packages" in (distutils.util.__file__ or ""):
        raise SystemExit("distutils is not the standard library's; set SETUPTOOLS_USE_DISTUTILS")
    import click
    import ruamel.yaml
    import setuptools._distutils.util
    import str_to_bool
    import yaml

    yaml12 = ruamel.yaml.YAML(typ="safe", pure=True)
    tools: dict[str, tuple[str, Callable[[str], object]]] = {
        "distutils": (f"stdlib {platform.python_version()}", _as_bool(distutils.util.strtobool)),
        "setuptools": (metadata.version("setuptools"), setuptools._distutils.util.strtobool),
        "python-strtobool": (metadata.version("python-strtobool"), str_to_bool.str_to_bool),
        "configparser": (f"stdlib {platform.python_version()}", _configparser),
        "click": (metadata.version("click"), lambda text: click.BOOL.convert(text, None, None)),
        "pyyaml-1.1": (metadata.version("PyYAML"), yaml.safe_load),
        "ruamel-yaml-1.2": (metadata.version("ruamel.yaml"), yaml12.load),
    }
    out = {
        "captured": datetime.date.today().isoformat(),
        "python": platform.python_version(),
        "corpus": "hand-written inputs (scripts/capture_oracles.py); answers are the tools' own",
        "tools": {
            name: {"version": version, "results": run(parse)}
            for name, (version, parse) in tools.items()
        },
    }
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, ensure_ascii=False, indent=1, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
