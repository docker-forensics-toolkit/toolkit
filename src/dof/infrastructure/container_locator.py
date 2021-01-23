from functools import lru_cache
from pathlib import Path
from typing import List
from model.container import Container, ConfigVersion
from infrastructure.logging import warn, trace


class ContainerLocator:
    """This class locates Container files and loads their data into a higher level Container object"""

    def __init__(self, docker_home: Path):
        self.docker_home = docker_home

    def container_by_name(self, name: str) -> Container:
        """Gets a container by the (human-readable) name it was given by the user.

        Raises a RuntimeError when there is no container with this name.

        Note this name may start with a slash (/) due to historic reasons.
        See also: https://github.com/moby/moby/issues/29997"""
        for container in self.all_containers():
            if container.name == f"/{name}" or container.name == name:
                return container
        raise RuntimeError(f"Could not find a container named: {name}")

    def container_by_name_or_id(self, name_or_id) -> Container:
        """Gets a container by id or the (human-readable) name it was given by the user.

        Raises a RuntimeError when there is no container with this name.

        Note this name may start with a slash (/) due to historic reasons.
        See also: https://github.com/moby/moby/issues/29997"""
        for container in self.all_containers():
            if container.name == name_or_id or container.name == "/" + name_or_id:
                return container
            elif name_or_id in container.id:
                return container
        raise RuntimeError(f"Could not find a container with name or id: {name_or_id}")

    def containers_based_on_image_with_id(self, id: str) -> List[Container]:
        """Returns a list of containers that use the image with the given id."""
        return [cont for cont in self.all_containers() if cont.image_id == f"sha256:{id}"]

    def _check_containers_folder(self):
        if not self.container_root_folder().exists():
            raise RuntimeError(f"Containers folder does not exist at: {str(self.container_root_folder())}. "
                               + "Are you sure this is a Docker Host?")

    @lru_cache(maxsize=1)
    def all_containers(self) -> List[Container]:
        """Gets all containers from the container root folder"""
        self._check_containers_folder()
        return [self.__container_from_folder(container_folder) for container_folder in self.__all_container_folders()]

    def running_containers(self) -> List[Container]:
        """Gets all containers that are in a Runing state"""
        self._check_containers_folder()
        return [container for container in self.all_containers() if container.state == "running"]

    def not_running_containers(self) -> List[Container]:
        """Gets all containers that are not in a Runing state"""
        self._check_containers_folder()
        return [container for container in self.all_containers() if container.state != "running"]

    def container_root_folder(self) -> Path:
        """Returns the folder where docker keeps container data"""
        return self.docker_home / "containers"

    def __container_from_folder(self, container_folder: Path) -> Container:
        """Constructs a container object from the given folders metadatata """
        if (container_folder / "config.v2.json").exists():
            trace(f"Reading container config from: {container_folder}")
            config_file = Container.from_v2_config(container_folder)
            return Container(self.docker_home, config_file, ConfigVersion.Two)
        elif (container_folder / "config.json").exists():
            raise NotImplemented("Docker Versions prior to 17.06 are note supported.")
        else:
            raise RuntimeError("No or unknown version of container config encountered.")

    def __all_container_folders(self) -> List[Path]:
        """Returns a list of folders that contain container metadata."""
        folders = []
        for subdirectory in self.container_root_folder().iterdir():
            absolute_path = self.container_root_folder() / subdirectory
            if absolute_path.is_dir():
                folders.append(absolute_path)
        return folders
