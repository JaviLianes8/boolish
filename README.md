# strtobool

Parse a string into a boolean. A typed, dependency-free stand-in for
`distutils.util.strtobool`, which was removed from the standard library in Python 3.12.

## Install

```
pip install strtobool
```

## Usage

```python
from strtobool import strtobool

strtobool("yes")     # True
strtobool("Off")     # False
strtobool("  1 ")    # True  (space and case are ignored)
strtobool("maybe")   # ValueError
```

Give a default to get it back instead of an error:

```python
strtobool("maybe", False)   # False
```

Read a flag straight from the environment. A missing variable falls back to the
default; a set-but-nonsense value raises, so a misconfigured flag fails loudly:

```python
from strtobool import getenv_bool

getenv_bool("ENABLE_CACHE", False)
```

Bring your own vocabulary:

```python
from strtobool import BoolRules, strtobool

spanish = BoolRules(true={"sí", "verdadero"}, false={"no", "falso"})
strtobool("SÍ", rules=spanish)   # True
```

## Why

The standard library's `strtobool` was the quiet default for reading boolean flags and
environment variables. It was deprecated in 3.10 and removed in 3.12, and the dedicated
packages that filled the gap have gone unmaintained for years. This is the same idea,
kept small: real `bool` results, type hints, no dependencies, and the environment helper
most projects ended up writing by hand.

## License

MIT — see [LICENSE](LICENSE).

## Links

- Website — https://lianes8studio.com
- GitHub — https://github.com/JaviLianes8
- LinkedIn — https://www.linkedin.com/in/jlianes/
