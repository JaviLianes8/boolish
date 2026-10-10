import importlib.resources

import strtobool

# The public API. This list is the contract; the test below fails if the module drifts.
PUBLIC_API = ["BoolRules", "DEFAULT", "getenv_bool", "strtobool"]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(strtobool.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in strtobool.__all__:
        assert hasattr(strtobool, name)


def test_version_is_a_three_part_string() -> None:
    parts = strtobool.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("strtobool").joinpath("py.typed").is_file()
