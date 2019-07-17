from commands.list_images import ListImagesCommand
from infrastructure.image_locator import ImageLocator


def test_groups_images_by_name(docker_home):
    image_locator = ImageLocator(docker_home)
    container_locator = StubContainerLocator()
    command = ListImagesCommand(image_locator, container_locator)

    result = command._all_images_grouped_by_name()

    assert image_locator.image_by_tag('httpd:2.4.38-alpine') in result['httpd']
    assert image_locator.image_by_tag('mysql:8.0.16') in result['mysql']


class StubContainerLocator:
    def init(self):
        pass

    def containers_based_on_image_with_id(self, image_id):
        return []


class StubImageLocator:
    def __init__(self, stub_images):
        self.stub_images = stub_images

    def all_images(self):
        return self.stub_images
