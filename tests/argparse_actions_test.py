from argparse import Namespace, ArgumentError
from pathlib import Path

import pytest

from argparse_actions import ValidatePathAction

def test_validate_path_action_with_nargs_doesnt_work():
    with pytest.raises(ValueError):
        ValidatePathAction("test", "test", nargs=3)


def test_validate_path_action_with_valid_path():
    action = ValidatePathAction("test", "test")
    namespace = Namespace()
    action(None, namespace, "/")

    assert namespace.test == Path("/")


def test_validate_path_action_with_invalid_path():
    action = ValidatePathAction("test", "test")
    namespace = Namespace()
    with pytest.raises(ArgumentError):
        action(None, namespace, "/doesnotexist")

