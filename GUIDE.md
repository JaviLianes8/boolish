# boolish guide

A practical tour of `boolish`. It reads loose, human boolean-ish input and gives you a
real `bool`. Everything here uses the standard library only; the package has no runtime
dependencies.

## The two front doors

`strtobool` takes a string, exactly like the stdlib function it replaces.

```python
from boolish import strtobool

strtobool("yes")  # True
strtobool("  Off ")  # False (case and surrounding space never matter)
strtobool("maybe")  # raises NotBooleanError
strtobool("maybe", False)  # False (a default suppresses the error)
```

`to_bool` is the broader door: it accepts `bool`, `int`, `float`, `str` and `None`.

```python
from boolish import to_bool

to_bool(True)  # True
to_bool(1)  # True
to_bool(0.0)  # False
to_bool("on")  # True
to_bool(None, False)  # False (default returned)
to_bool(None)  # raises NotBooleanError
```

Booleans pass through untouched. The numbers `0` and `1` map to `False` and `True`.
Strings go through the vocabulary. Anything else returns the default you pass, or raises.

## Strict vs lenient

Both `strtobool` and `to_bool` take `strict`, which defaults to `True`.

- **Strict** (the default) matches the normalised vocabulary exactly, and only accepts
  `0` or `1` for numbers.
- **Lenient** (`strict=False`) also folds accents before matching, so `"Sí"` resolves
  against a rule spelled `"si"`, and treats any non-zero, finite number as `True`.

```python
to_bool(5)  # raises: 5 is not 0 or 1
to_bool(5, strict=False)  # True

strtobool("Sí", rules=MULTILINGUAL)  # raises in strict mode
strtobool("Sí", rules=MULTILINGUAL, strict=False)  # True
```

## Predicates that never raise

`is_truthy` and `is_falsy` return a plain `bool` and never raise. They are mirrors, not
negations: anything unrecognised is `False` for both.

```python
from boolish import is_truthy, is_falsy

is_truthy("yes")  # True
is_truthy("maybe")  # False
is_falsy("off")  # True
is_falsy("maybe")  # False
```

Reach for these inside an `if` where an unparseable value should simply count as "no".

## Vocabularies

A `BoolRules` is a pair of case-insensitive word sets. Two are ready to use:

- `DEFAULT` understands `y/yes/t/true/on/1/enable/enabled` and the matching falsy forms.
- `MULTILINGUAL` adds common yes/no and true/false words across English, Spanish, French,
  German, Italian and Portuguese.

```python
from boolish import DEFAULT, MULTILINGUAL, strtobool

strtobool("enabled")  # True
strtobool("oui", rules=MULTILINGUAL)  # True
```

Build your own, or layer a few words on top of an existing set with `extend`:

```python
from boolish import BoolRules, DEFAULT, strtobool

pirate = DEFAULT.extend(true={"aye"}, false={"nay"})
strtobool("aye", rules=pirate)  # True
strtobool("yes", rules=pirate)  # True (the base words are still there)

custom = BoolRules(true={"up"}, false={"down"})
```

A word listed as both truthy and falsy is rejected at construction, as is a pair that
would collide once accents are folded.

## Environment variables

`getenv_bool` reads a variable and parses it. A missing variable returns the default; a
set-but-nonsense value raises, so a misconfigured flag fails loudly instead of silently
defaulting.

```python
from boolish import getenv_bool

getenv_bool("ENABLE_CACHE", False)
getenv_bool("ENABLE_CACHE", False, rules=MULTILINGUAL, strict=False)
```

## Errors

`NotBooleanError` is raised for input that cannot be understood. It subclasses
`BoolishError`, which subclasses `ValueError`, so existing `except ValueError` handlers
keep working while new code can catch exactly this library's failures. The offending
value is kept on the `value` attribute.

```python
from boolish import NotBooleanError, strtobool

try:
    strtobool("banana")
except NotBooleanError as error:
    print(error.value)  # 'banana'
```

## Command line

Installing the package adds a `boolish` console script.

```
boolish yes            # prints "true", exits 0
boolish off            # prints "false", exits 1
boolish --quiet on     # prints nothing, exits 0 (read the exit code)
boolish --lenient --rules multilingual Si
boolish --true aye --false nay aye
```

The exit code is `0` for true and `1` for false, so the command drops straight into a
shell conditional:

```
if boolish --quiet "$FLAG"; then echo enabled; fi
```

An unrecognised value prints a message to stderr and exits `1`. Run `boolish --help` for
the full list of options and examples, and `boolish --version` to print the version.
