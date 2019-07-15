import argparse
import os
import sys
import pytest
import subprocess

from pathlib import Path

# Add the dof library to the PYTHONPATH - otherwise imports will fail.
path_of_this_file = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path_of_this_file + '/../src/dof')
path_of_this_file = Path(path_of_this_file)


# This is so we can pass --image-mountpoint to the pytest command for integration tests
def pytest_addoption(parser):
    """ attaches optional cmd-line args to the pytest machinery """
    parser.addoption("--image-mountpoint", action="append", default=[],
                     help="The directory where a docker host image is mounted")


@pytest.fixture(scope='package')
def image_mountpoint(tmpdir_factory) -> Path:
    tmp_path = tmpdir_factory.mktemp("files_for_integration_test")
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-mountpoint')
    args, _ = parser.parse_known_args()
    if not args.image_mountpoint:
        gzip_with_files_for_integration_tests = path_of_this_file / "files_for_integration_test.tgz"
        if os.getuid() != 0:
            # Fakeroot is required to create some character devices that reside in the /var/lib/docker folder.
            subprocess.run(f"fakeroot tar xzf {gzip_with_files_for_integration_tests}",
                           shell=True,
                           check=True,
                           cwd=tmp_path)
        else:
            subprocess.run(f"tar xzf {gzip_with_files_for_integration_tests}",
                           shell=True,
                           check=True,
                           cwd=tmp_path)
        return Path(tmp_path)
    if not os.path.exists(args.image_mountpoint):
        raise ValueError(f"The given mountpoint does not seem to exist: {args.image_mountpoint}")
    return Path(args.image_mountpoint)


@pytest.fixture()
def docker_home(image_mountpoint: Path) -> Path:
    return image_mountpoint / "var" / "lib" / "docker"
