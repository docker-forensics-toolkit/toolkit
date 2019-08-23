from pathlib import Path


class ArgumentsStub:
    def __init__(self, image_mountpoint: Path):
        self._image_mountpoint = image_mountpoint

    @property
    def image_mountpoint(self):
        return self._image_mountpoint

    @property
    def docker_home(self):
        return self.image_mountpoint / "var" / "lib" / "docker"

