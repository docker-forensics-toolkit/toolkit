from pathlib import Path

from infrastructure.docker_binaries_locator import DockerBinariesLocator


def test_finding_docker_binaries(image_mountpoint: Path):
    repo = DockerBinariesLocator(image_mountpoint)

    binaries = repo.find_docker_binaries()

    assert binaries.relative_docker_daemon_path == Path() / "usr" / "bin" / "dockerd"
    assert binaries.relative_docker_client_path == Path() / "usr" / "bin" / "docker"


def test_extracting_versions(image_mountpoint: Path):
    repo = DockerBinariesLocator(image_mountpoint)

    binaries = repo.find_docker_binaries()
    versions = binaries.extract_docker_version()

    assert versions.docker_client_version == "18.09.6-ce"
    # daemon version does not work yet, because the version string does not seem to be part of
    # the binary file for unknown reasons. Maybe it's part of a .so file?
    assert versions.docker_daemon_version == "Unknown"










