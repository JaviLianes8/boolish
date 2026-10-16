# boolish improvement round

This was the plan of the 0.2.0 round. Version 1.0.0 changed some of the behaviour it
describes; the CHANGELOG lists every difference.

A ranked list of substantial, coherent improvements for this round. Every item is
additive: the existing public API (`strtobool`, `getenv_bool`, `BoolRules`, `DEFAULT`)
keeps its exact signatures and behaviour, so nothing downstream breaks.

## Starting point

Before this round `boolish` parsed strings only. It exposed `strtobool` (string in,
`bool` out, optional default), `getenv_bool` (read a variable, loud on a bad value),
and `BoolRules` (a custom truthy/falsy vocabulary) with a single `DEFAULT` ruleset that
mirrored the stdlib `strtobool` words. There was no way to coerce a value that was not
already a string, no non-raising predicate, no typed error, no accent handling, no ready
multilingual vocabulary, and no command line entry point.

## Ranked improvements

1. **`to_bool`: coerce any boolean-ish value, not just strings.** A single front door
   that accepts `bool`, `int`, `float`, `str` and `None`. Booleans pass through, `1`/`0`
   map directly, strings go through the vocabulary, and unknown values either return a
   default or raise. This is the function most callers actually want when a config value
   might arrive as any type.

2. **Strict and lenient modes.** Every parsing entry point takes `strict`. Strict (the
   default, so existing behaviour is untouched) matches the exact normalised vocabulary
   and only accepts `0`/`1` for numbers. Lenient folds accents (so `sí` matches `si`) and
   treats any non-zero number as true, for human-entered or loosely typed input.

3. **Richer default vocabulary.** `DEFAULT` now also understands `enable`/`enabled` and
   `disable`/`disabled` on top of the classic `y/yes/t/true/on/1` and
   `n/no/f/false/off/0`. Purely additive: strings that used to raise now parse.

4. **`MULTILINGUAL` ruleset.** A ready vocabulary covering common yes/no and
   true/false forms across English, Spanish, French, German, Italian and Portuguese,
   plus on/off and enabled/disabled. Opt in with `rules=MULTILINGUAL`.

5. **Configurable custom mappings via `BoolRules.extend`.** Add words on top of an
   existing ruleset without rebuilding it from scratch, for example
   `DEFAULT.extend(true={"aye"}, false={"nay"})`. Returns a new frozen ruleset.

6. **Typed errors.** `NotBooleanError` (a subclass of the existing `ValueError`, so
   `except ValueError` still catches it) lets callers catch exactly this library's
   failure. `BoolishError` is the package base class.

7. **Non-raising predicates `is_truthy` / `is_falsy`.** Return a plain `bool` and never
   raise: `is_truthy` is true only for recognised truthy input, `is_falsy` only for
   recognised falsy input, and both are false for anything unknown. Ideal inside `if`
   statements where a default of "no" is the right call.

8. **Accent, case and whitespace handling.** Surrounding whitespace and case were
   already ignored. Lenient mode adds Unicode accent folding built on the standard
   library only, so `Sí`, `OUI` and `  Ja  ` all resolve without a bespoke vocabulary.

9. **A command line interface.** A `boolish` console script (argparse) converts an input
   to a bool, with `--strict`/`--lenient`, custom `--true`/`--false` words, `--rules
   multilingual`, a `--quiet` exit-code-only mode, `--version`, and a `--help` full of
   runnable examples. Errors go to stderr with exit code 1; false exits 1, true exits 0,
   so it drops straight into shell conditionals.

10. **Documentation: full docstrings and a guide.** Every public name gets a complete
    docstring with examples, and `GUIDE.md` walks through parsing, modes, custom
    vocabularies, environment variables and the CLI.

11. **Contract and real end-to-end tests.** A contract test pins the complete promise of
    every public name across vocabularies and modes, and a real end-to-end test
    pip-installs the package into a throwaway virtual environment and drives the actual
    installed `boolish` console script over `subprocess`.

## Explicitly out of scope

- No breaking changes, no renames, no removed names.
- No third-party dependencies (accent folding uses `unicodedata` from the stdlib).
- No network, PyPI upload or release from this round.
