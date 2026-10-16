"""Seeded fuzz and size checks: no crash, no hang, no quadratic blow-up."""

from __future__ import annotations

import random
import time
import unicodedata
from collections.abc import Callable

import pytest

from boolish import (
    CLASSIC,
    DEFAULT,
    MULTILINGUAL,
    BoolishError,
    BoolRules,
    NotBooleanError,
    is_falsy,
    is_truthy,
    strtobool,
    to_bool,
)
from boolish._normalize import fold

WORDS = sorted(MULTILINGUAL.true | MULTILINGUAL.false)
PIECES = [
    *WORDS,
    " ",
    "\t",
    "\n",
    chr(0xA0),
    chr(0x3000),
    chr(0x301),
    chr(0x303),
    chr(0x130),
    chr(0xFF59),
    chr(0x0),
    chr(0x202E),
    chr(0xD800),
    chr(0x10FFFF),
    "ß",
    "Ã",
    "-",
    ".",
]
SEEDS = range(8)


def _text(rng: random.Random) -> str:
    parts = rng.choices(PIECES, k=rng.randint(0, 4))
    text = "".join(parts)
    if rng.random() < 0.5:
        text = text.upper() if rng.random() < 0.5 else text.title()
    return text


@pytest.mark.parametrize("seed", SEEDS)
def test_strings_only_ever_give_a_bool_or_the_default(seed: int) -> None:
    rng = random.Random(seed)
    missing = object()
    for _ in range(3000):
        text = _text(rng)
        for rules in (CLASSIC, DEFAULT, MULTILINGUAL):
            strict = strtobool(text, missing, rules=rules)
            lenient = strtobool(text, missing, rules=rules, strict=False)
            assert strict is missing or type(strict) is bool
            assert lenient is missing or type(lenient) is bool
            if strict is not missing:
                assert lenient is strict, text
            assert is_truthy(text, rules=rules) is (strict is True)
            assert is_falsy(text, rules=rules, strict=False) is (lenient is False)
            if strict is missing:
                with pytest.raises(NotBooleanError):
                    strtobool(text, rules=rules)


@pytest.mark.parametrize("seed", SEEDS)
def test_folding_is_idempotent(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(3000):
        text = _text(rng)
        assert fold(fold(text)) == fold(text), ascii(text)


@pytest.mark.parametrize("seed", SEEDS)
def test_any_value_coerces_or_raises_not_boolean(seed: int) -> None:
    rng = random.Random(seed)
    makers: list[Callable[[], object]] = [
        lambda: rng.randint(-3, 3),
        lambda: rng.choice([0.0, -0.0, 1.0, 0.5, float("nan"), float("inf"), 1e308]),
        lambda: rng.getrandbits(rng.randint(1, 20000)) * rng.choice([1, -1]),
        lambda: _text(rng),
        lambda: rng.choice([None, True, False, b"1", [], {}, (1,), object(), 2j]),
    ]
    for _ in range(2000):
        value = rng.choice(makers)()
        for strict in (True, False):
            try:
                result = to_bool(value, strict=strict)  # type: ignore[call-overload]
            except NotBooleanError as error:
                assert error.value is value
                assert len(str(error)) < 120
            else:
                assert type(result) is bool
            truthy = is_truthy(value, strict=strict)  # type: ignore[arg-type]
            falsy = is_falsy(value, strict=strict)  # type: ignore[arg-type]
            assert not (truthy and falsy)


@pytest.mark.parametrize("seed", SEEDS)
def test_random_rulesets_build_or_refuse_cleanly(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(300):
        true = {_text(rng) for _ in range(rng.randint(0, 5))}
        false = {_text(rng) for _ in range(rng.randint(0, 5))}
        try:
            rules = BoolRules(true, false)
        except BoolishError:
            continue
        for word in rules.true:
            assert strtobool(word, rules=rules) is True
            assert strtobool(word.upper(), None, rules=rules, strict=False) in (True, None)
        for word in rules.false:
            assert strtobool(f" {word} ", rules=rules) is False


def _seconds(func: Callable[..., object], *args: object, **kwargs: object) -> float:
    start = time.perf_counter()
    func(*args, **kwargs)
    return time.perf_counter() - start


@pytest.mark.parametrize(
    "build",
    [
        lambda n: " " * n + "yes" + " " * n,
        lambda n: "y" + chr(0x301) * n,
        lambda n: chr(0xFF59) * n,
        lambda n: "Ã" * n,
    ],
    ids=["spaces", "marks", "fullwidth", "accented"],
)
def test_huge_input_is_handled_in_linear_time(build: object) -> None:
    small = build(100_000)  # type: ignore[operator]
    large = build(1_000_000)  # type: ignore[operator]
    for strict in (True, False):
        quick = _seconds(strtobool, small, None, strict=strict)
        slow = _seconds(strtobool, large, None, strict=strict)
        assert slow < 2.0
        assert slow < max(quick, 0.001) * 40


def test_a_huge_vocabulary_builds_in_linear_time() -> None:
    words = [f"w{n}" for n in range(200_000)]
    assert _seconds(BoolRules, words, ["no"]) < 5.0


def _reference_fold(text: str) -> str:
    """The folding rule written the slow, obvious way: whole-string NFKD."""

    def strip(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        return "".join(ch for ch in decomposed if not unicodedata.combining(ch))

    return strip(strip(text).lower()).strip()


@pytest.mark.parametrize("seed", SEEDS)
def test_chunked_folding_equals_whole_string_folding(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(200):
        text = "".join(_text(rng) for _ in range(rng.randint(1, 700)))
        assert fold(text) == _reference_fold(text)
