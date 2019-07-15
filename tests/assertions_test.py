from assertions import is_any_valid_docker_container_id


def test_is_any_valid_docker_container_id():
    assert is_any_valid_docker_container_id("a2b1afc9683c05200b15f0d5f008c27f185503ab1300fd8ce229b107cf460481")
    # too short
    assert not is_any_valid_docker_container_id("2b1afc9683c05200b15f0d5f008c27f185503ab1300fd8ce229b107cf460481")
    # too long
    assert not is_any_valid_docker_container_id("aa2b1afc9683c05200b15f0d5f008c27f185503ab1300fd8ce229b107cf460481")
    # invalid character
    assert not is_any_valid_docker_container_id("a&2b1afc9683c05200b15f0d5f008c27f185503ab1300fd8ce229b107cf460481")
