from pathlib import Path

from decorators import requires_root, requires_docker_home_argument
from infrastructure.container_locator import ContainerLocator
from infrastructure.docker_binaries_locator import DockerBinariesLocator
from infrastructure.image_locator import ImageLocator
from infrastructure.logging import info, highlight
from infrastructure.swarm_config_locator import SwarmConfigLocator


@requires_root
@requires_docker_home_argument
def run_status_command(args, image_mountpoint: Path, docker_home: Path):
    container_locator = ContainerLocator(docker_home)
    binaries_locator = DockerBinariesLocator(image_mountpoint)
    image_locator = ImageLocator(docker_home)
    swarm_config_locator = SwarmConfigLocator(docker_home)

    DockerHostStatusCommand(image_locator, container_locator, binaries_locator, swarm_config_locator).execute()


class DockerHostStatusCommand:
    """Outputs information about the status of a Docker Host, such as:
    * Version of the Docker Binaries
    * Number of containers found
    * Number of running containers
    * Number of images found"""

    def __init__(self,
                 image_locator: ImageLocator,
                 container_locator: ContainerLocator,
                 binaries_locator: DockerBinariesLocator,
                 swarm_config_locator: SwarmConfigLocator):
        self.swarm_config_locator = swarm_config_locator
        self.image_locator = image_locator
        self.binaries_locator = binaries_locator
        self.containers = container_locator

    def execute(self):
        docker_binaries = self.binaries_locator.find_docker_binaries()
        docker_versions = docker_binaries.extract_docker_version()
        number_of_running_containers = str(len(self.containers.running_containers()))
        number_of_total_containers = str(len(self.containers.all_containers()))
        number_of_images = str(len(self.image_locator.all_images()))
        number_of_images_without_repo = str(len(self.image_locator.images_without_repository()))

        info(f"Found Docker client with version: {highlight(docker_versions.docker_client_version)} "
             f"at {docker_binaries.absolute_docker_client_path}")
        if self.swarm_config_locator.is_part_of_swarm:
            info(f"This host is part of a Docker Swarm with the Node ID {highlight(self.swarm_config_locator.node_id)}")
        else:
            info(f"This host is not part of a Docker Swarm")
        info(f"{highlight(number_of_running_containers)} containers running on this machine")
        info(f"{highlight(number_of_total_containers)} total containers found on this machine")
        info(f"{highlight(number_of_images)} images found on this machine")
        info(f"{highlight(number_of_images_without_repo)} images belong to no repository")
