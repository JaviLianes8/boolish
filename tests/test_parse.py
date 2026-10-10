import pytest

from strtobool import BoolRules, strtobool


@pytest.mark.parametrize("value", ["y", "yes", "t", "true", "on", "1"])
def test_truthy_words_parse_to_true(value: str) -> None:
    assert strtobool(value) is True


@pytest.mark.parametrize("value", ["n", "no", "f", "false", "off", "0"])
def test_falsy_words_parse_to_false(value: str) -> None:
    assert strtobool(value) is False


def test_matching_ignores_case_and_surrounding_space() -> None:
    assert strtobool("  YES ") is True
    assert strtobool("Off") is False


def test_an_unknown_value_raises() -> None:
    with pytest.raises(ValueError, match="maybe"):
        strtobool("maybe")


def test_a_default_is_returned_instead_of_raising() -> None:
    assert strtobool("maybe", None) is None
    assert strtobool("maybe", "skip") == "skip"


def test_custom_rules_replace_the_vocabulary() -> None:
    spanish = BoolRules(true={"sí", "verdadero"}, false={"no", "falso"})
    assert strtobool("SÍ", rules=spanish) is True
    assert strtobool("Falso", rules=spanish) is False


def test_rules_that_overlap_are_rejected() -> None:
    with pytest.raises(ValueError):
        BoolRules(true={"yes", "on"}, false={"on", "no"})


def test_the_result_is_a_real_bool() -> None:
    assert isinstance(strtobool("yes"), bool)
