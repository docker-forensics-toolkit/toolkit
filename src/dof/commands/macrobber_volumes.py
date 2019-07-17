from pathlib import Path

from decorators import requires_docker_home_argument, requires_root
from infrastructure.container_locator import ContainerLocator
from infrastructure.logging import trace
from infrastructure.mac_robber import mac_robber_folder


@requires_root
@requires_docker_home_argument
def run_macrobber_on_volumes(args, image_mountpoint: Path, docker_home: Path):
    container_name_or_id = args.container_name_or_id
    container_locator = ContainerLocator(docker_home)
    container = container_locator.container_by_name_or_id(container_name_or_id)

    for volume in container.volumes:
        source = image_mountpoint / volume.source[1:]
        trace(f"running mac_robber_folder(folder={str(source)} bind_mount_path={str(volume.destination)})")
        mac_times = mac_robber_folder(source, bind_mount_path=volume.destination)
        for line in mac_times:
            print(line)




