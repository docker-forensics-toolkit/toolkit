import subprocess
from pathlib import Path

from decorators import requires_root, requires_docker_home_argument
from infrastructure.container_locator import ContainerLocator
from infrastructure.logging import trace


@requires_root
@requires_docker_home_argument
def show_container_logfile(args, image_mountpoint: Path, docker_home: Path):
    editor = args.editor or "less"
    container_name_or_id = args.container_name_or_id

    container_locator = ContainerLocator(docker_home)
    container = container_locator.container_by_name_or_id(container_name_or_id)
    if container.logging_driver() in ["local", "json-file"]:
        logfile = container.get_path_to_logfile(image_mountpoint)
        trace(f"Opening file {logfile}")
        subprocess.check_call([editor, logfile])
    else:
        raise Exception(f"This container uses an unsupported logging driver: {container.logging_driver()}")

