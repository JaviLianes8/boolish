# boolish guide

A practical tour of `boolish`: it reads loose, human boolean-ish input and gives a real
`bool`. Every `pycon` block below is run by the test suite.

## The two front doors

`strtobool` takes a string, like the stdlib function it replaces. Surrounding whitespace
and case never matter. Without a default an unrecognised string raises
`NotBooleanError`; with one, the default comes back (whatever object it is).

```pycon
>>> from boolish import strtobool
>>> strtobool("yes"), strtobool("\tOFF\n")
(True, False)
>>> strtobool("maybe", None) is None
True
```

A value that is not a `str` is a programming error and raises `TypeError`, default or
not:

```pycon
>>> strtobool(1)
Traceback (most recent call last):
...
TypeError: strtobool expects a str, not int
```

`to_bool` accepts any `BoolLike` value: `bool`, `int`, `float`, `str` or `None`.
Booleans pass through, `0` and `1` (and `0.0`, `1.0`) map to `False` and `True`, strings
go through the vocabulary. Anything else, `None` included, returns the default or raises
`NotBooleanError`. Subclasses such as `IntEnum` members are read by their value.

```pycon
>>> from boolish import to_bool
>>> to_bool(True), to_bool(1), to_bool(0.0), to_bool(" on ")
(True, True, False, True)
>>> to_bool(None, "unset"), to_bool([1], "unset")
('unset', 'unset')
```

## Strict and lenient

Every parsing function takes a keyword-only `strict`, `True` by default.

- **Strict** matches the trimmed, lower-cased text against the vocabulary exactly and
  accepts only `0` and `1` as numbers.
- **Lenient** (`strict=False`) also folds the text: compatibility forms such as
  full-width letters are decomposed and accents removed, so `"Sí"` matches `si` and
  `"NÃO"` matches `nao`. Any other finite number counts as `True`. `NaN` and infinities
  are never boolean.

```pycon
>>> from boolish import MULTILINGUAL
>>> to_bool(5, None), to_bool(5, strict=False), to_bool(float("nan"), None, strict=False)
(None, True, None)
>>> strtobool("Sí", None, rules=MULTILINGUAL), strtobool("Sí", rules=MULTILINGUAL, strict=False)
(None, True)
```

Strings are never read as numbers: `"2"` is not boolean in either mode.

## Predicates that never raise

`is_truthy` and `is_falsy` return a plain `bool` for any input and never raise. They are
mirrors, not negations: anything unrecognised is `False` for both.

```pycon
>>> from boolish import is_falsy, is_truthy
>>> is_truthy("yes"), is_truthy("maybe"), is_falsy("maybe"), is_falsy(0)
(True, False, False, True)
```

## Vocabularies

A `BoolRules` holds two `frozenset` attributes, `true` and `false`, normalised on
construction. Three are ready to use:

| Name | Words |
| --- | --- |
| `CLASSIC` | `y yes t true on 1` and `n no f false off 0`: the removed stdlib function's twelve |
| `DEFAULT` | `CLASSIC` plus `enable enabled` and `disable disabled` |
| `MULTILINGUAL` | `DEFAULT` plus `active ok si verdadero oui vrai ja wahr vero sim verdadeiro` and `inactive falso non faux nein falsch nao` |

`DEFAULT` is used when no `rules` is passed; `BoolRules()` with no arguments equals
`CLASSIC`. `MULTILINGUAL` stores words without accents: in strict mode the input must be
written without them too, in lenient mode either spelling matches. One-letter answers
other than `y` and `n` (such as `s` for Spanish *sí* or `j` for German *ja*) are left
out on purpose: a single letter means different things in different languages.

Build your own, or layer words on top of one with `extend` (the original is unchanged):

```pycon
>>> from boolish import BoolRules, DEFAULT
>>> BoolRules(true=["Up"], false=["down"])
BoolRules(true=['up'], false=['down'])
>>> strtobool("AYE", rules=DEFAULT.extend(true={"aye"}))
True
```

A word on both sides raises `BoolishError`, as does a pair that collides once accents are
folded (`sí` true and `si` false). A bare string instead of a collection of words, or a
word that is not a string, raises `TypeError` (a string would otherwise be split into
letters). Rulesets are frozen, hashable, comparable and picklable.

## Environment variables

`getenv_bool(name, default=None, *, rules=DEFAULT, strict=True)` reads a variable. Unset
returns `default`. Set to anything unrecognised, the empty string included, raises
`NotBooleanError` whose `variable` attribute and message name the variable. The message
gives only the length of the value, never the value itself, since environment variables
often hold secrets; the whole value is on the error's `value` attribute:

```pycon
>>> import os
>>> from boolish import NotBooleanError, getenv_bool
>>> os.environ["GUIDE_FLAG"] = ""
>>> try:
...     getenv_bool("GUIDE_FLAG", False)
... except NotBooleanError as error:
...     print(error.variable, "|", error)
GUIDE_FLAG | environment variable 'GUIDE_FLAG': a value of 0 characters is not a recognised boolean
```

To treat an empty variable as false, say so: `DEFAULT.extend(false={""})`.

## Errors

| Error | Raised when |
| --- | --- |
| `NotBooleanError` | a value has no boolean meaning and no default was given; `getenv_bool` on a set but unrecognised variable |
| `BoolishError` | base class of the above; raised directly for a ruleset with a word on both sides, or two words that are equal once folded |
| `TypeError` | `strtobool` given a non-string; a ruleset given a bare string or a non-string word |

`BoolishError` subclasses `ValueError`. `NotBooleanError` keeps the whole input on
`value` but its message shows at most the first 32 characters, a size for huge integers
and only the (escaped) type name for other objects, so a message never carries a
payload; for an environment variable it gives only the length of the value.

## Command line

The `boolish` console script (also `python -m boolish`) prints `true` or `false` and
exits `0` for true, `1` for false and `2` for an unrecognised value or a usage error.
Errors go to stderr as one line starting with `boolish:`.

```console
$ boolish on
true
$ boolish --rules classic enabled
boolish: 'enabled' is not a recognised boolean
$ boolish --quiet off
$ boolish --true aye --true yarr --false nay YARR
true
```

Options: `--strict` (default) or `--lenient`, `--rules classic|default|multilingual`,
repeatable `--true WORD` and `--false WORD`, `-q`/`--quiet`, `--version`, `--help`.

## How boolish compares

Checked against the real tools (answers captured in `tests/fixtures/oracles.json`):

- `distutils.util.strtobool` (Python 3.11), setuptools' copy and python-strtobool 1.0.3
  accept exactly `CLASSIC`'s words; they do not ignore surrounding whitespace, and the
  stdlib one returns `1`/`0`.
- `configparser` accepts `1 yes true on` and `0 no false off`; click 8.5 accepts the
  `CLASSIC` words and also reads an empty or blank value as false, which boolish refuses.
- PyYAML (YAML 1.1) reads `yes no true false on off` in their three spellings as
  booleans; ruamel.yaml (YAML 1.2 core schema) only `true` and `false`.

No vocabulary of boolish ever gives the opposite answer to any of these tools.

## Upgrading from 0.1.0

The CHANGELOG's 1.0.0 section lists every difference. The ones most likely to matter:
`DEFAULT` gained `enable(d)` and `disable(d)` (pass `rules=CLASSIC` for the 0.1.0
words); errors are `NotBooleanError` and `BoolishError`, still `ValueError`;
`strtobool` raises `TypeError` for anything that is not a `str`, `bytes` included and
even with a default; `BoolRules` refuses a bare string and a true and a false word that
become equal once folded (such as `sí` and `si`).
