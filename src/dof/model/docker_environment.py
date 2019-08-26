import subprocess
from pathlib import Path

from infrastructure.logging import trace


class DockerVersions:
    def __init__(self, docker_client_version: str, docker_daemon_version: str):
        self.docker_client_version = docker_client_version
        self.docker_daemon_version = docker_daemon_version


class DockerBinaries:
    def __init__(self, image_mountpoint: Path, docker_client_path: Path, docker_daemon_path: Path):
        self.image_mountpoint = image_mountpoint
        self.relative_docker_daemon_path = docker_daemon_path
        self.relative_docker_client_path = docker_client_path

    __docker_version_number_pattern = r"^[[:digit:]]{2}\.[[:digit:]]{2}\.[[:digit:]]*\-[[:alpha:]]{2}$"

    def extract_docker_version(self) -> DockerVersions:
        if self.relative_docker_client_path:
            client_version = self.__extract_version_string(self.absolute_docker_client_path)
        else:
            client_version = "Unknown"
        return DockerVersions(client_version,
                              "Unknown")
        # TODO: For some reason there doesn't seem to be a version string in the daemon executable, find another way
        # to extract the version?

    def __extract_version_string(self, a_binary: Path):
        """Uses the command line tools 'strings' and 'grep' to extract a Docker Version number.
           This only matches the new version pattern Docker introduced in March 2017: Year.Month.Minor-Edition"""
        strings_command = ["strings", str(a_binary)]
        trace(f'Running: {" ".join(strings_command)}')
        p1 = subprocess.Popen(strings_command, stdout=subprocess.PIPE)
        grep_command = ["grep", "-E", self.__docker_version_number_pattern]
        trace(f'Output piped to: {" ".join(grep_command)}')
        p2 = subprocess.Popen(grep_command, stdin=p1.stdout,
                              stdout=subprocess.PIPE)
        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        communicate_ = p2.communicate()[0]
        output = communicate_.decode("utf-8").strip()
        return output

    @property
    def absolute_docker_client_path(self):
        if self.relative_docker_client_path:
            return self.image_mountpoint / self.relative_docker_client_path
        else:
            return None

