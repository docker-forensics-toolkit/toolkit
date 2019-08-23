from pathlib import Path

from commands.list_containers import ListContainerCommandLinearStyle
from infrastructure.container_locator import ContainerLocator


def test_listing_images_as_list(docker_home: Path, capsys):
    capsys.readouterr()
    container_locator = ContainerLocator(docker_home)
    ListContainerCommandLinearStyle(container_locator).execute()
    captured_output = capsys.readouterr()

    print(captured_output.out)

    lines = captured_output.out.split("\n")
    assert len(lines) == 28
    assert lines[0] == "/apache"
    assert lines[12] == ""
    assert lines[13] == "/mysql"

