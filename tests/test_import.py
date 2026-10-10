import strtobool


def test_version_is_exposed() -> None:
    assert strtobool.__version__ == "0.1.0"
