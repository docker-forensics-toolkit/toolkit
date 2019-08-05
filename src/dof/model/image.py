from typing import List

from infrastructure.container_locator import ContainerLocator


class Image:
    def __init__(self, id: str, config_file: dict, repository: str, tags: List[str]):
        self.config_file = config_file
        self.__id = id
        self.__tags = tags
        self.__repository = repository

    @property
    def id(self) -> str:
        return self.__id

    @property
    def tags(self) -> List[str]:
        return self.__tags

    @property
    def repository(self) -> str:
        return self.__repository

    @property
    def repository_string(self) -> str:
        return self.__repository or "<none>"

    @property
    def build_history(self):
        return self.config_file['history']

    @property
    def parent_image(self):
        return self.config_file['config']['Image']

    def used_in_containers(self, container_locator: ContainerLocator):
        return container_locator.containers_based_on_image_with_id(self.id)



    def __eq__(self, other):
        return self.id == other.id
