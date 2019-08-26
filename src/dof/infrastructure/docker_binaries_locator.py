from pathlib import Path

from model.docker_environment import DockerBinaries


class DockerBinariesLocator:
    """This class locates Docker binary files and loads their data into a higher level DockerBinaries object"""

    __common_binary_locations = [
        Path() / "usr" / "local" / "bin",
        Path() / "usr" / "bin",
        Path() / "bin"
    ]

    def __init__(self, image_mountpoint: Path):
        self.__image_mountpoint = image_mountpoint

    def find_docker_binaries(self) -> DockerBinaries:
        """"Looks for the 'docker' binary in typical binary directories such as: /usr/bin and /usr/local/bin"""
        client_path = None
        daemon_path = None
        for possible_path in self.__common_binary_locations:
            if (self.__image_mountpoint / possible_path / "docker").exists():
                client_path = possible_path / "docker"
            if (self.__image_mountpoint / possible_path / "dockerd").exists():
                daemon_path = possible_path / "dockerd"
        return DockerBinaries(self.__image_mountpoint, client_path, daemon_path)

