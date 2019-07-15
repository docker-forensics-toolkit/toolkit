import re


def is_any_valid_docker_container_id(string: str) -> bool:
    """Because Docker IDs may change when the image is rebuilt, we assert only the hash form of the ID, not the exact
    value."""
    return re.fullmatch("^[0-9a-f]{64}$", string) is not None


