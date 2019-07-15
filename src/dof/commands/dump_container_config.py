from pathlib import Path
from pprint import pprint

from decorators import requires_root, requires_docker_home_argument
from infrastructure.container_locator import ContainerLocator
from model.container import Container


@requires_root
@requires_docker_home_argument
def run_dump_container_config(args, docker_home: Path, image_mountpoint: Path):
    containers = ContainerLocator(docker_home)
    container: Container = containers.container_by_name_or_id(args.container_name_or_id)
    pprint(container.config_file)

