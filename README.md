# boolish

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

Read loose, human boolean-ish strings and values as a real `bool`. A typed,
dependency-free stand-in for `distutils.util.strtobool`, which Python deprecated in 3.10
and removed in 3.12 ([PEP 632](https://peps.python.org/pep-0632/)), plus a broader
coercer, non-raising predicates, an environment helper, a multilingual vocabulary and a
command line tool.

## Install

```
pip install boolish
```

Python 3.10 or newer, no dependencies.

## Quick start

```pycon
>>> from boolish import strtobool
>>> strtobool("yes"), strtobool("  Off "), strtobool("enabled")
(True, False, True)
>>> strtobool("maybe", False)
False
>>> strtobool("maybe")
Traceback (most recent call last):
...
boolish.NotBooleanError: 'maybe' is not a recognised boolean
```

`NotBooleanError` subclasses `ValueError`, so code written for the stdlib function keeps
catching it. Coerce more than strings with `to_bool`, or ask without ever raising:

```pycon
>>> from boolish import is_falsy, is_truthy, to_bool
>>> to_bool(1), to_bool(0.0), to_bool("on"), to_bool(None, False)
(True, False, True, False)
>>> is_truthy("maybe"), is_falsy("maybe"), is_falsy("no")
(False, False, True)
```

Read a flag from the environment. Unset gives the default; a set but unreadable value
raises, naming the variable, so a misconfigured flag fails loudly:

```pycon
>>> import os
>>> from boolish import getenv_bool
>>> os.environ["CACHE"] = "off"
>>> getenv_bool("CACHE", True), getenv_bool("UNSET_FLAG_FOR_README", True)
(False, True)
```

Pick or build a vocabulary. `CLASSIC` is exactly the stdlib function's twelve words,
`DEFAULT` adds `enable(d)`/`disable(d)`, `MULTILINGUAL` adds Spanish, French, German,
Italian and Portuguese; lenient mode (`strict=False`) folds accents:

```pycon
>>> from boolish import CLASSIC, DEFAULT, MULTILINGUAL
>>> strtobool("enabled", None, rules=CLASSIC) is None
True
>>> strtobool("Sí", rules=MULTILINGUAL, strict=False), strtobool("nein", rules=MULTILINGUAL)
(True, False)
>>> pirate = DEFAULT.extend(true={"aye"}, false={"nay"})
>>> strtobool("AYE", rules=pirate)
True
```

## Command line

```console
$ boolish yes
true
$ boolish --rules multilingual --lenient NÃO
false
$ boolish --true aye --false nay aye
true
```

The exit code is `0` for true, `1` for false and `2` for an unrecognised value or a
usage error, so `if boolish --quiet "$FLAG"; then ...; fi` works in a shell.
`python -m boolish` runs the same tool.

## Why

`distutils.util.strtobool` was the quiet default for reading flags. It returned `1` or
`0` rather than a `bool`, did not ignore surrounding spaces, and is gone since Python
3.12. Other packages fill part of the gap: setuptools keeps a copy in its private
`setuptools._distutils.util`; python-strtobool 1.0.3 copies the function and returns a
`bool`; str2bool (last release 1.1, December 2017) knows no `on`/`off` and returns
`None` for unknown input. boolish is checked word by word against the stdlib function,
setuptools, python-strtobool, `configparser`, click, PyYAML (YAML 1.1) and ruamel.yaml
(YAML 1.2) and never gives an answer that contradicts any of them; it adds typed results
and errors, defaults, non-string input, an environment helper and a CLI.

## Learn more

- [GUIDE](https://github.com/JaviLianes8/boolish/blob/main/GUIDE.md): modes, vocabularies,
  errors, the CLI and how boolish compares with other parsers.
- [CHANGELOG](https://github.com/JaviLianes8/boolish/blob/main/CHANGELOG.md): what changed
  in each release, including the upgrade notes for 1.0.0.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/boolish/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
