# boolish

Interpret loose, human boolean-ish strings and values as a real `bool`. A typed,
dependency-free stand-in for `distutils.util.strtobool`, which was removed from the
standard library in Python 3.12, with a broader coercer, non-raising predicates, a
multilingual vocabulary and a command line interface.

## Install

```
pip install boolish
```

## Usage

```python
from boolish import strtobool

strtobool("yes")  # True
strtobool("Off")  # False
strtobool("  1 ")  # True  (space and case are ignored)
strtobool("maybe")  # NotBooleanError (a ValueError subclass)
```

Give a default to get it back instead of an error:

```python
strtobool("maybe", False)  # False
```

Coerce more than strings with `to_bool`. It accepts `bool`, `int`, `float`, `str` and
`None`:

```python
from boolish import to_bool

to_bool(1)  # True
to_bool(0.0)  # False
to_bool("on")  # True
to_bool(None, False)  # False
```

Use the non-raising predicates where unknown input should just count as "no":

```python
from boolish import is_truthy, is_falsy

is_truthy("yes")  # True
is_truthy("maybe")  # False
is_falsy("off")  # True
```

Go lenient to fold accents and treat any non-zero number as true:

```python
from boolish import MULTILINGUAL, strtobool, to_bool

strtobool("Sí", rules=MULTILINGUAL, strict=False)  # True
to_bool(5, strict=False)  # True
```

Read a flag straight from the environment. A missing variable falls back to the default;
a set-but-nonsense value raises, so a misconfigured flag fails loudly:

```python
from boolish import getenv_bool

getenv_bool("ENABLE_CACHE", False)
```

Bring your own vocabulary, or extend a built-in one:

```python
from boolish import BoolRules, DEFAULT, strtobool

spanish = BoolRules(true={"sí", "verdadero"}, false={"no", "falso"})
strtobool("SÍ", rules=spanish)  # True

pirate = DEFAULT.extend(true={"aye"}, false={"nay"})
strtobool("aye", rules=pirate)  # True
```

## Command line

Installing the package adds a `boolish` console script. It prints `true` or `false` and
sets the exit code (`0` for true, `1` for false), so it drops into shell conditionals.

```
boolish yes                              # prints "true", exits 0
boolish --quiet on                       # prints nothing, exits 0
boolish --lenient --rules multilingual Si
boolish --true aye --false nay aye

if boolish --quiet "$FLAG"; then echo enabled; fi
```

Run `boolish --help` for every option and more runnable examples.

## Why

The standard library's `strtobool` was the quiet default for reading boolean flags and
environment variables. It was deprecated in 3.10 and removed in 3.12, and the dedicated
packages that filled the gap have gone unmaintained for years. This keeps the same idea
small: real `bool` results, type hints, no dependencies, and the helpers most projects
ended up writing by hand.

## Learn more

- [GUIDE.md](GUIDE.md) walks through parsing, modes, custom vocabularies, the environment
  helper and the CLI.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
