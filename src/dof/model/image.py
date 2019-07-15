from typing import List


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

    def __eq__(self, other):
        return self.id == other.id
