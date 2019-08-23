import re
from pathlib import Path

from commands.docker_host_status import run_status_command
from stubs import ArgumentsStub

ANSI_ESCAPE_CHARACTERS_REGEX = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')


def test_docker_host_status(image_mountpoint: Path, capsys):
    capsys.readouterr()
    run_status_command(ArgumentsStub(image_mountpoint))

    captured_output = capsys.readouterr()

    lines = list(map(strip_ansi_escapes, captured_output.out.split("\n")))
    assert lines[0].startswith("Found Docker client with version: 18.09.6-ce at ")
    assert lines[1] == "This host is not part of a Docker Swarm"
    assert lines[2] == "1 containers running on this machine"
    assert lines[3] == "2 total containers found on this machine"
    assert lines[4] == "2 images found on this machine"
    assert lines[5] == "0 images belong to no repository"



def strip_ansi_escapes(line):
    """Strips ANSI escape sequences from a string."""
    return ANSI_ESCAPE_CHARACTERS_REGEX.sub('', str(line))
