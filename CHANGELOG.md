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
- `NotBooleanError.variable`: the environment variable a `getenv_bool` error came from;
  the message names it too.
- `python -m boolish`, and `--rules classic` on the command line.
- The vocabularies are checked against the stdlib function, setuptools' copy,
  python-strtobool, `configparser`, click, PyYAML, ruamel.yaml, the YAML 1.1 and 1.2.2
  specifications and the CLDR yes/no words.

### Changed

- Exit code `2` (was `1`) for an unrecognised value on the command line, so a false
  answer and an error can be told apart; usage errors already exited `2`.
- `strtobool` raises `TypeError` for a value that is not a `str`, even with a default
  (0.1.0 raised `AttributeError`).
- Error messages show at most the first 32 characters of a string, a size for huge
  integers and only the type name for other objects; the whole input stays on `value`.
  `to_bool` on an integer of more than 4300 digits used to fail (Python 3.11 and newer)
  with the `ValueError` of `repr`; it now raises `NotBooleanError`.
- `BoolRules` refuses a bare `str`, `bytes` or `bytearray` (it was split into letters)
  and a word that is not a `str`, with `TypeError`; `extend` too. Its `true` and `false`
  attributes are typed `frozenset[str]` and its constructor takes any iterable.
- `BoolRules` no longer exposes `true_folded` and `false_folded` as fields or
  constructor arguments; `repr` lists the words sorted.
- Lenient folding also handles compatibility forms (full-width letters) and marks added
  by lower-casing.
- `to_bool` reads `int` and `float` subclasses by their value, so a subclass cannot
  change the answer through `__eq__`; `strtobool` ignores overridden `strip`/`lower`.
- `getenv_bool(name, rules=..., strict=...)` without a default now type-checks.
- `BoolRules`, `BoolishError` and `NotBooleanError` report `boolish` as their module.
- The version lives in one place; `pyproject.toml` reads it.

### Upgrading from 0.1.0 (the previous release on PyPI)

- `DEFAULT` also accepts `enable`, `enabled`, `disable` and `disabled`; pass
  `rules=CLASSIC` to keep the 0.1.0 words.
- Errors are `NotBooleanError` and `BoolishError`, both still `ValueError`.
- New: `to_bool`, `is_truthy`, `is_falsy`, `strict=False`, `MULTILINGUAL`,
  `BoolRules.extend`, `strict` and `rules` on `getenv_bool`, and the command line tool.

## [0.2.0] - not published


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
