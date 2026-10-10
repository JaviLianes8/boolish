import pytest

from strtobool import getenv_bool


def test_reads_and_parses_the_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEATURE_X", "true")
    assert getenv_bool("FEATURE_X") is True


def test_missing_variable_returns_none_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEATURE_X", raising=False)
    assert getenv_bool("FEATURE_X") is None


def test_missing_variable_returns_the_given_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEATURE_X", raising=False)
    assert getenv_bool("FEATURE_X", False) is False


def test_an_unparseable_value_is_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEATURE_X", "banana")
    with pytest.raises(ValueError):
        getenv_bool("FEATURE_X", False)
