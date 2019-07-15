import json
from pathlib import Path
from typing import List

from model.image import Image


class ImageLocator:
    """This class locates Image files and loads their data into a higher level Image object"""

    @staticmethod
    def read_config_file(config_file_path: Path) -> dict:
        with config_file_path.open() as file:
            return json.load(file)

    def __init__(self, docker_home: Path):
        self.docker_home = docker_home
        if (self.docker_home / "image" / "overlay2").exists():
            self.driver = "overlay2"
        elif (self.docker_home / "image" / "aufs").exists():
            self.driver = "aufs"
        else:
            raise RuntimeError("Unsupported Docker version or storage driver.")

    def images_root_folder(self) -> Path:
        return self.docker_home / "image" / self.driver / "imagedb" / "content" / "sha256"

    def repository_data_file(self) -> Path:
        return self.docker_home / "image" / self.driver / "repositories.json"

    def all_images(self) -> List[Image]:
        """Returns all the images."""
        if not self.images_root_folder().exists():
            raise RuntimeError(f"Images folder does not exist at: {str(self.images_root_folder())}. "
                            + "Are you sure this is a Docker Host?")
        return [self.__image_from_file(image_file) for image_file in self.__all_image_files()]

    def images_without_repository(self) -> List[Image]:
        """Returns all the images that don't belong to a repository."""
        return [image for image in self.all_images() if image.repository is None]

    def image_by_tag_or_id(self, image_tag_or_id) -> Image:
        """Finds images by tag or id"""
        for image in self.all_images():
            if image_tag_or_id in image.id:
                return image
            elif image_tag_or_id in image.tags:
                return image
        raise RuntimeError(f"No such image found with tag or id: {image_tag_or_id}")

    def image_by_tag(self, name_and_tag) -> Image:
        """Finds an image by tag"""
        for image in self.all_images():
            if name_and_tag in image.tags:
                return image
        raise RuntimeError(f"No such image found with name and tag: {name_and_tag}")

    def image_by_id(self, id) -> Image:
        """Finds an image by id"""
        for image in self.all_images():
            if image.id == id or f"sha256:{image.id}" == id:
                return image
        raise RuntimeError(f"No such image found with id: {id}")

    def __all_image_files(self) -> List[Path]:
        return [file for file in self.images_root_folder().iterdir() if file.is_file()]

    def __image_from_file(self, image_config_file) -> Image:
        image_tags, repository = self.__image_tags_and_name_from_repository_data(image_config_file.name)
        return Image(image_config_file.name, self.read_config_file(image_config_file), repository, image_tags)

    def __repository_data(self) -> dict:
        return self.read_config_file(self.repository_data_file())

    def __image_tags_and_name_from_repository_data(self, image_id: str) -> ([str], str):
        image_tags: List[str] = []
        repository_name = None
        repo_data = self.__repository_data()
        for name, tags in repo_data["Repositories"].items():
            for tag, hashcode in tags.items():
                if hashcode == f"sha256:{image_id}":
                    image_tags.append(tag)
                    repository_name = name
        return image_tags, repository_name




