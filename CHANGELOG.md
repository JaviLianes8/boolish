# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

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

## [0.1.0]

- `strtobool` with optional default, matching that ignores case and surrounding space.
- `getenv_bool` to read a flag from the environment, loud on a set-but-invalid value.
- `BoolRules` for a custom truthy/falsy vocabulary.
