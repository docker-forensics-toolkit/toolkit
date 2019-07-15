from pathlib import Path

from decorators import requires_root, requires_docker_home_argument
from infrastructure.container_locator import ContainerLocator
from infrastructure.logging import info
from model.container import Container


@requires_root
@requires_docker_home_argument
def run_list_containers(args, image_mountpoint: Path, docker_home: Path):
    # TODO: Write a test for this
    container_locator = ContainerLocator(docker_home)
    if args.style == "tabular":
        ListContainerCommandDockerTabularStyle(container_locator).execute()
    else:
        ListContainerCommandLinearStyle(container_locator).execute()


class ListContainerCommandDockerTabularStyle:
    """Outputs info about the containers found on the Docker Host in a tabular style similar to running 'docker ps'."""

    def __init__(self, container_locator: ContainerLocator):
        self.container_locator = container_locator

    @staticmethod
    def format_ports(container: Container) -> str:
        if not container.ports:
            return "<none>"
        return_value = ""
        for key, value in container.ports.items():
            for mapping in value:
                return_value += f'{mapping["HostIp"]}:{mapping["HostPort"]}->{key}'
        return return_value

    def execute(self):
        containers = self.container_locator.all_containers()
        table_format = "{:<12.12}    {:<50.50}    {:<10.10}    {:<25.25}    {:<30.30}"

        info(table_format.format("CONTAINER ID", "IMAGE",  "STATE", "PORTS", "NAMES"))
        for container in containers:
            info(table_format.format(container.id,
                                     container.image_tag,
                                     container.state,
                                     self.format_ports(container),
                                     container.name
                                     ))


class ListContainerCommandLinearStyle(object):
    """Outputs info about the containers found on the Docker Host in a linear style similar to running 'ifconfig'."""

    def __init__(self, container_locator: ContainerLocator):
        self.container_locator = container_locator

    def execute(self):
        containers = self.container_locator.running_containers()
        for container in containers:
            self.print_container(container)
        containers = self.container_locator.not_running_containers()
        for container in containers:
            self.print_container(container)

    @staticmethod
    def print_container(container: Container):
        print(container.name)
        print(f"\tID: {container.id}")
        print(f"\tState: {container.state}")
        print(f"\tRestart Policy: {container.restart_policy or '<none>'}")
        print(f"\tCreated: {container.creation_date}")
        print(f"\tImage: {container.image_tag}")
        print(f"\tImage ID: {container.image_id}")
        print(f"\tEntrypoint: {container.entrypoint}")
        print(f"\tCommand: {container.command}")
        print(f"\tStorage Driver: {container.storage_driver}")
        print(f"\tContainer Layer: {container.container_layer_folder}")
        if container.ports:
            print(f"\tPorts: {container.ports_to_string()}")
        else:
            print(f"\tPorts: <none>")
        for volume in container.volumes:
            if volume.source:
                print(f"\tVolume: Host folder '{volume.source}' mounted in in Container at '{volume.destination}'")
            else:
                print(f"\tVolume: at '{volume.destination}' is not mapped to any folder on the host system.")
        print("")
