import pytest

from main import select_command_and_run


def test_main():
    # Should throw no exception
    with pytest.raises(SystemExit):
        select_command_and_run(["","--help"])
