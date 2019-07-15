from commands.list_images import ListImagesCommand
from infrastructure.container_locator import ContainerLocator
from model.image import Image


def test_groups_images_by_name():
    image_locator = StubImageLocator([
        Image('1' * 64, {}, "foo", ["foo:1.25", "foo:latest"]),
        Image('2' * 64, {}, "bar", ["bar:1.23"]),
        Image('3' * 64, {}, "bar", ["bar:1.22"])
    ])
    container_locator = StubContainerLocator()
    command = ListImagesCommand(image_locator, container_locator)

    result = command._all_images_grouped_by_name()

    assert result == {
        "foo": [{
            "tags": "foo:1.25, foo:latest",
            "id": "1" * 64,
            "containers": "<none>"
        }],
        "bar": [{
            "tags": "bar:1.23",
            "id": "2" * 64,
            "containers": "<none>"
        },
            {
                "tags": "bar:1.22",
                "id": "3" * 64,
                "containers": "<none>"
            }]
    }


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
