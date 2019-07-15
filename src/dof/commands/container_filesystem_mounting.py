import argparse
from pathlib import Path
import tempfile

from decorators import requires_root, requires_docker_home_argument
from infrastructure.container_locator import ContainerLocator
from infrastructure.logging import info, highlight


@requires_root
@requires_docker_home_argument
def run_mount_container_command(args, image_mountpoint: Path, docker_home: Path):
    container_name_or_id = args.container_name_or_id
    container_fs_mountpoint = args.container_mountpoint or tempfile.mkdtemp()
    container_locator = ContainerLocator(docker_home)

    container = container_locator.container_by_name_or_id(container_name_or_id)

    mount_point = container.mount_container_filesystem(container_fs_mountpoint)
    info(f"Mounted container {container_name_or_id} at {highlight(mount_point)}")


