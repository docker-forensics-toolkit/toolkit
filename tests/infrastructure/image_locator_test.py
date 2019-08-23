from pathlib import Path

import pytest

from infrastructure.image_locator import ImageLocator
from model.image import Image


def test_locating_images(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    images = image_locator.all_images()

    assert len(images) == 2


def test_locating_images_fails():
    with pytest.raises(RuntimeError):
        ImageLocator(Path("/not/docker/"))


def test_locating_images_by_tag(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    image = image_locator.image_by_tag("mysql:8.0.16")

    assert "mysql:8.0.16" in image.tags

def test_image_history(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    image = image_locator.image_by_tag("mysql:8.0.16")

    assert len(image.build_history) == 20


def test_locating_images_by_tag_fails(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    with pytest.raises(RuntimeError):
        image_locator.image_by_tag("mysql:does-not-exist")


def test_locating_images_without_a_repository(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    images_without_repository = image_locator.images_without_repository()

    assert len(images_without_repository) == 0


def test_locating_images_by_tag_or_id(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    httpd_by_name: Image = image_locator.image_by_tag_or_id("httpd:2.4.38-alpine")
    httpd_by_id = image_locator.image_by_tag_or_id(httpd_by_name.id)

    assert httpd_by_id == httpd_by_name


def test_locating_images_by_name_or_id_fails(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    with pytest.raises(RuntimeError):
        image_locator.image_by_tag_or_id("httpd:does-not-exist")


def test_locating_image_by_id(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    image_by_id: Image = image_locator.image_by_id("c7109f74d339896c8e1a7526224f10a3197e7baf674ff03acbab387aa027882a")
    image_by_sha_id: Image = image_locator.image_by_id("sha256"
                                                       ":c7109f74d339896c8e1a7526224f10a3197e7baf674ff03acbab387aa027882a")

    assert image_by_id == image_by_sha_id


def test_locating_image_by_id_fails(docker_home: Path):
    image_locator = ImageLocator(docker_home)

    with pytest.raises(RuntimeError):
        image_locator.image_by_id("doesnotexistdoesnotexist")
