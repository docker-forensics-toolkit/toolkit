from pathlib import Path

from commands.list_images import ListImagesCommand
from infrastructure.container_locator import ContainerLocator
from infrastructure.image_locator import ImageLocator


def test_listing_images(docker_home: Path, capsys):
    capsys.readouterr()
    image_locator = ImageLocator(docker_home)
    container_locator = ContainerLocator(docker_home)
    ListImagesCommand(image_locator, container_locator).execute()
    captured_output = capsys.readouterr()

    print(captured_output.out)

    lines = captured_output.out.split("\n")
    assert lines[0] == "Repository: httpd"
    assert lines[1] == "\tId: 0c388cccfd046fb7f46560e6605e128f0bd0c2bb2f5858b84b0f16d1497e32a6"
    assert lines[2] == '\tTags: httpd:2.4.38-alpine,httpd@sha256:eb8ccf084cf3e80eece1add239effefd171eb39adbc154d33c14260d905d4060'
    assert lines[3] == '\tParent: sha256:28b12ae8c01f5f97789dc1db105fc06471edafa27b921666e80e15fe8ba3742f'
    assert lines[4] == '\tContainer: /apache'
    assert lines[5] == ''
    assert lines[6] == 'Repository: mysql'
    assert lines[7] == '\tId: c7109f74d339896c8e1a7526224f10a3197e7baf674ff03acbab387aa027882a'
    assert lines[8] == '\tTags: mysql:8.0.16,mysql@sha256:415ac63da0ae6725d5aefc9669a1c02f39a00c574fdbc478dfd08db1e97c8f1b'
    assert lines[9] == '\tParent: sha256:3953c878942d2b2b30352e6d245b066bcb9f23df7d60912609909caa9fd62cc7'
    assert lines[10] == '\tContainer: /mysql'


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
