from pathlib import Path

import pytest

from model.container import Volume
from infrastructure.container_locator import ContainerLocator
from assertions import is_any_valid_docker_container_id


def test_loading_containers(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    containers = container_repo.all_containers()

    assert len(containers) == 2


def test_load_running_containers(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    containers = container_repo.running_containers()

    assert len(containers) == 1
    assert containers[0].name == "/apache"


def test_loading_container_by_name(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    apache_container = container_repo.container_by_name("apache")

    # Docker puts a / prefix into the config file, for unknown reasons.
    # There's an open issue to remove this: https://github.com/moby/moby/issues/29997
    assert apache_container.name == "/apache"
    assert apache_container.image_tag == "httpd:2.4.38-alpine"
    assert is_any_valid_docker_container_id(apache_container.id)
    assert apache_container.state == "running"
    assert apache_container.storage_driver == "overlay2"
    # This ID will change when you test with a real mounted container file system instead of the zipped one.
    assert apache_container.container_layer_id == "45513121980a2da435c87f16fcb271fd4a939f58e483a9ad6aae04cd760df796"
    assert apache_container.image_id == "sha256:0c388cccfd046fb7f46560e6605e128f0bd0c2bb2f5858b84b0f16d1497e32a6"
    assert apache_container.container_folder == docker_home / "containers" / apache_container.id
    assert apache_container.creation_date == "2019-06-20T16:51:36.605799443Z"
    assert apache_container.entrypoint is None
    assert apache_container.command == ["httpd-foreground"]
    assert apache_container.storage_driver_folder == docker_home / "overlay2"
    assert apache_container.container_layer_folder == \
           docker_home / "overlay2" / apache_container.container_layer_id / "diff"
    assert apache_container.container_layer_work_folder == \
           docker_home / "overlay2" / apache_container.container_layer_id / "work"
    assert apache_container.image_layer_folders == "l/Q6RK3MBIY2MI3CL3JHWPJFBUNH:" \
                                                             "l/6PQIU4AUXMUTWWXOXEAAEMBH4Y:" \
                                                             "l/YOHCGPDPMO6XYCX2J3YMVT4276:" \
                                                             "l/AZGTVIGVJYBXA74JPRZ6Z5DBBO:" \
                                                             "l/U7ZEXQXNLXX6342N7BGPI5FSOG:" \
                                                             "l/IKX4BXCGITBJOBMK6OQLYBSAG6"
    assert apache_container.get_path_to_logfile(Path("/tmp/foo")) == \
           Path("/tmp/foo/var/lib/docker/containers/f54149276f6f3e5d8e6da7b3e4abdf58542d515ba9a12836e04cf6058f22e1c4/"
                "f54149276f6f3e5d8e6da7b3e4abdf58542d515ba9a12836e04cf6058f22e1c4-json.log")
    assert apache_container.ports == {"80/tcp": None}
    assert apache_container.restart_policy == "always"

    mysql_container = container_repo.container_by_name("mysql")

    assert mysql_container.name == "/mysql"
    assert mysql_container.image_tag == "mysql:8.0.16"
    assert is_any_valid_docker_container_id(mysql_container.id)
    assert mysql_container.state == "dead"
    assert Volume(source="/var/mysql/datadir", destination="/var/lib/mysql") in mysql_container.volumes


def test_loading_container_by_name_or_id(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    apache_container = container_repo.container_by_name_or_id("apache")
    container_retrieved_with_slash = container_repo.container_by_name_or_id("/apache")
    # This ID will change when you test with a real mounted container file system instead of the zipped one.
    apache_container_id = "f54149276f6f3e5d8e6da7b3e4abdf58542d515ba9a12836e04cf6058f22e1c4"
    container_retrieved_with_id = container_repo.container_by_name_or_id(apache_container_id)

    container_retrieved_with_partial_id = container_repo.container_by_name_or_id(apache_container_id[:10])

    assert apache_container == container_retrieved_with_slash
    assert apache_container == container_retrieved_with_id
    assert apache_container == container_retrieved_with_partial_id
    assert apache_container.name == "/apache"


def test_loading_container_by_name_fails(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    with pytest.raises(RuntimeError):
        container_repo.container_by_name("does not exist")


def test_loading_container_by_name_or_id_fails(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    with pytest.raises(RuntimeError):
        container_repo.container_by_name_or_id("does not exist")


def test_loading_containers_not_running(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    assert len(container_repo.not_running_containers()) == 1
    assert container_repo.not_running_containers()[0].name == "/mysql"


def test_loading_containers_based_on_image(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    mysql_image_id = "c7109f74d339896c8e1a7526224f10a3197e7baf674ff03acbab387aa027882a"
    containers = container_repo.containers_based_on_image_with_id(mysql_image_id)

    assert len(containers) == 1
    assert containers[0].name == "/mysql"


def test_loading_containers_based_on_image_fails(docker_home: Path):
    container_repo = ContainerLocator(docker_home)

    httpd_image_id = "no such image"
    containers = container_repo.containers_based_on_image_with_id(httpd_image_id)

    assert len(containers) == 0


def test_docker_home_folder_does_not_exist():
    container_repo = ContainerLocator(Path("/not/a/docker/home/"))

    with pytest.raises(RuntimeError):
        container_repo.container_by_name("does not exist")
