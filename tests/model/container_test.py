from pathlib import Path

from model.container import Container, ConfigVersion


def test_container_can_derive_its_container_layer_id_file_path():
    container_id = "1" * 63
    driver = "overlay2"
    docker_home = Path("/var/lib/docker")
    container = Container(docker_home, {'ID': container_id, 'Driver': driver}, ConfigVersion.Two)

    assert container._container_layer_id_file == \
           docker_home / "image" / driver / "layerdb" / "mounts" / container_id / "mount-id"
