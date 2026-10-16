# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-16

The first stable release. The public surface is `strtobool`, `to_bool`, `is_truthy`,
`is_falsy`, `getenv_bool`, `BoolRules`, `CLASSIC`, `DEFAULT`, `MULTILINGUAL`,
`BoolLike`, `BoolishError`, `NotBooleanError` and the `boolish` command; their names,
signatures, defaults and error types follow semantic versioning from here on.

### Added

- `CLASSIC`: exactly the twelve words of the removed `distutils.util.strtobool`, equal
  to `BoolRules()`. Use it for the 0.1.0 vocabulary.
- `NotBooleanError.variable`: the environment variable a `getenv_bool` error came from.
- `python -m boolish`, and `--rules classic` on the command line.
- The vocabularies are checked against the stdlib function, setuptools' copy,
  python-strtobool, `configparser`, click, PyYAML, ruamel.yaml, the YAML 1.1 and 1.2.2
  specifications and the CLDR yes/no words.

### Upgrading from 0.1.0 (the previous release on PyPI)

Every behaviour that differs from 0.1.0:

- `DEFAULT` also accepts `enable`, `enabled`, `disable` and `disabled`; pass
  `rules=CLASSIC` to keep the 0.1.0 words.
- Errors are `NotBooleanError` (unrecognised input) and `BoolishError` (a bad
  ruleset), both still `ValueError`. Messages show at most the first 32 characters of
  the input (0.1.0 echoed it whole); `getenv_bool` errors name the variable and give
  only the length of its value, which may be a secret.
- `strtobool` raises `TypeError` for a value that is not a `str`, with or without a
  default. In 0.1.0, `bytes` raised `ValueError` or returned the default, and other
  types raised `AttributeError`.
- `BoolRules` raises `TypeError` for a bare `str`, `bytes` or `bytearray` (0.1.0 split
  `"yes"` into the words `y`, `e`, `s`) and for a word that is not a `str`.
- `BoolRules` raises `BoolishError` for a true and a false word that become equal once
  accents and compatibility forms are folded, such as `sí` and `si` (0.1.0 accepted
  them), because lenient matching could not tell them apart.
- `BoolRules.true` and `BoolRules.false` are typed `frozenset[str]`; the constructor
  takes any iterable of words. `repr` lists the words sorted.
- `BoolRules`, `BoolishError`, `NotBooleanError` and the public functions report
  `boolish` as their module.
- New: `CLASSIC`, `to_bool`, `is_truthy`, `is_falsy`, `strict=False`, `MULTILINGUAL`,
  `BoolRules.extend`, `strict` and `rules` on `getenv_bool`, `NotBooleanError.value` and
  `.variable`, and the `boolish` command (also `python -m boolish`).

### Changed since the unpublished 0.2.0

- Exit code `2` (was `1`) for an unrecognised value on the command line, so a false
  answer and an error can be told apart; usage errors already exited `2`. The `--help`
  examples are now all runnable and the `--lenient` help no longer promises numbers
  (the command reads its value as text).
- `to_bool` on an integer of more than 4300 digits failed (Python 3.11 and newer) with
  the `ValueError` of `repr`; it now raises `NotBooleanError`.
- `BoolRules` keeps its folded vocabularies out of the dataclass fields and the
  constructor (they were the public `true_folded` and `false_folded`).
- Lenient folding also handles compatibility forms (full-width letters), runs in linear
  time on long input, and stops as soon as the input cannot fit the longest word.
- Subclasses of `str`, `int` and `float` are read by their plain value, whatever methods
  they override; objects that only pretend to be one (a mock with a `spec`) are not
  boolean. Type names in messages are escaped.
- The command keeps its exit code when stdout or stderr is closed, escapes and bounds
  argument errors, and prints `--help` on any console encoding.
- `getenv_bool(name, rules=..., strict=...)` without a default now type-checks.
- The version lives in one place; `pyproject.toml` reads it.

## [0.2.0] - not published

### Added

- `to_bool` coerces any boolean-ish value (`bool`, `int`, `float`, `str`, `None`), not
  only strings.
- `is_truthy` and `is_falsy`: non-raising predicates that are mirrors, not negations.
- Strict and lenient modes on every parsing entry point. Lenient folds accents and treats
  any non-zero number as true; strict (the default) keeps the prior behaviour.
- `MULTILINGUAL` ruleset covering English, Spanish, French, German, Italian and
  Portuguese yes/no and true/false forms.
- `BoolRules.extend` layers extra words onto an existing ruleset without rebuilding it.
- Richer `DEFAULT` vocabulary: `enable`/`enabled` and `disable`/`disabled`.
- Typed errors: `NotBooleanError` and its base `BoolishError`, both subclasses of
  `ValueError`.
- A `boolish` command line interface with strict/lenient, custom words, a multilingual
  vocabulary, a quiet exit-code-only mode, `--version` and `--help` with examples.
- `GUIDE.md` and expanded docstrings on every public name.

## [0.1.0] - 2026-10-10

- `strtobool` with optional default, matching that ignores case and surrounding space.
- `getenv_bool` to read a flag from the environment, loud on a set-but-invalid value.
- `BoolRules` for a custom truthy/falsy vocabulary.
