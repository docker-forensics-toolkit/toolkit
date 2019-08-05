from collections import defaultdict
from pathlib import Path

from decorators import requires_root, requires_docker_home_argument
from infrastructure.container_locator import ContainerLocator
from infrastructure.image_locator import ImageLocator


@requires_root
@requires_docker_home_argument
def run_list_images(args, image_mountpoint: Path,  docker_home: Path):
    # TODO: Write a test for this
    image_locator = ImageLocator(docker_home)
    container_locator = ContainerLocator(docker_home)
    ListImagesCommand(image_locator, container_locator).execute()


class ListImagesCommand:
    """Outputs info about the images found on the Docker Host."""
    def __init__(self, image_locator: ImageLocator, container_locator: ContainerLocator):
        self.container_locator = container_locator
        self.image_locator = image_locator

    def _all_images_grouped_by_name(self) -> dict:
        return_value = defaultdict(list)
        for image in self.image_locator.all_images():
            return_value[image.repository_string].append(image)
        return return_value

    def execute(self):
        images_grouped_by_repository = self._all_images_grouped_by_name()
        for repository_name in sorted(images_grouped_by_repository.keys()):
            print(f"Repository: {repository_name}")
            for image in images_grouped_by_repository[repository_name]:
                container_names = [container.name for container in image.used_in_containers(self.container_locator)]
                print("\tId:", image.id)
                print("\tTags:", ",".join(image.tags) if image.tags else "<none>"),
                print("\tParent:", image.parent_image)
                print("\tContainer:", ",".join(container_names) if container_names else "<none>")
            print("")


