import importlib.resources

import boolish

# The public API. This list is the contract; the test below fails if the module drifts.
PUBLIC_API = ["BoolRules", "DEFAULT", "getenv_bool", "strtobool"]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(boolish.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in boolish.__all__:
        assert hasattr(boolish, name)


def test_version_is_a_three_part_string() -> None:
    parts = boolish.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("boolish").joinpath("py.typed").is_file()
