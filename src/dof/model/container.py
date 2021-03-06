import collections
import json
from enum import Enum, auto
from pathlib import Path
import subprocess
from typing import List

from infrastructure.logging import trace

Volume = collections.namedtuple('Volume', 'source destination')


class ConfigVersion(Enum):
    One = auto()
    Two = auto()


class Container:
    def __init__(self, docker_home: Path, config_file: dict, config_version: ConfigVersion):
        self.docker_home = docker_home
        self.config_file = config_file
        self.config_version = config_version

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def from_v2_config(container_folder: Path):
        container_file = container_folder / "config.v2.json"
        container_config = Container.__read_container_config(container_file)
        host_config = Container.__read_host_config(container_folder)
        container_config['HostConfig'] = host_config
        return container_config


    @staticmethod
    def __read_container_config(container_file):
        trace(f"Reading container config from: {str(container_file)}")
        with container_file.open() as file:
            container_config = json.load(file)
        return container_config

    @staticmethod
    def __read_host_config(container_folder):
        host_file = container_folder / "hostconfig.json"
        trace(f"Reading container host config from: {str(host_file)}")
        with host_file.open() as file:
            host_config = json.load(file)
        return host_config

    def mount_container_filesystem(self, container_mountpoint: Path, image_mountpoint: Path) -> Path:
        """Tries to mount the container filesystem using the 'mount' command."""
        if self.storage_driver != "overlay2":
            raise NotImplementedError("Mounting container filesystems is only supported for overlay2 storage driver")
        command = ["mount", "-t", "overlay", "overlay", "-r", "-o",
                   f"lowerdir={self.image_layer_folders}:"
                   f"{self.container_layer_folder}",
                   str(container_mountpoint)]
        trace(f'Running: {" ".join(command)}')
        subprocess.check_call(command, cwd=str(self.storage_driver_folder))
        for volume in self.volumes:
            if volume.source:
                volume_dest = container_mountpoint / volume.destination[1:]
                command = ["mount", "--bind", str(image_mountpoint / volume.source[1:]), str(volume_dest)]
                trace(f'Running: {" ".join(command)}')
                subprocess.check_call(command)
                print(f"Mounted volume {volume.destination}")
        return container_mountpoint

    @property
    def id(self):
        return self.config_file["ID"]

    @property
    def name(self):
        return self.config_file["Name"]

    @property
    def container_folder(self):
        return self.docker_home / "containers" / self.id

    @property
    def creation_date(self):
        return self.config_file['Created']

    @property
    def state(self) -> str:
        if self.config_file["State"]["Running"]:
            return "running"
        else:
            return "dead"

    @property
    def restart_policy(self) -> str:
        return self.config_file['HostConfig']['RestartPolicy']['Name']

    @property
    def entrypoint(self):
        return self.config_file['Config']['Entrypoint']

    @property
    def command(self):
        return self.config_file['Config']['Cmd']

    @property
    def container_layer_id(self) -> str:
        with self._container_layer_id_file.open() as file:
            return file.read()

    @property
    def storage_driver_folder(self) -> Path:
        return self.docker_home / self.storage_driver

    @property
    def container_layer_folder(self) -> Path:
        if self.storage_driver == "overlay2":
            return self.storage_driver_folder / self.container_layer_id / "diff"
        elif self.storage_driver == "aufs":
            return self.storage_driver_folder / "diff" / self.container_layer_id
        else:
            raise NotImplemented(f"Unsupported storage driver {self.storage_driver}")

    @property
    def container_layer_work_folder(self) -> Path:
        return self.storage_driver_folder / self.container_layer_id / "work"

    @property
    def image_layer_folders(self) -> str:
        with (self.storage_driver_folder / self.container_layer_id / "lower").open() as lower_file:
            return lower_file.read()

    @property
    def _container_layer_id_file(self) -> Path:
        return self.docker_home / "image" / self.storage_driver / "layerdb" / "mounts" / self.id / "mount-id"

    def get_path_to_logfile(self, image_mountpoint: Path) -> Path:
        if self.logging_driver() == "json-file":
            relative_logfile_path = self.config_file['LogPath'][1:]
            return image_mountpoint / relative_logfile_path
        elif self.logging_driver() == "local":
            return self.container_folder / "local-logs" / "container.log"

    @property
    def storage_driver(self) -> str:
        return self.config_file["Driver"]

    @property
    def ports(self) -> dict:
        return self.config_file["NetworkSettings"]["Ports"]

    @property
    def image_tag(self) -> str:
        return self.config_file["Config"]["Image"]

    @property
    def image_id(self) -> str:
        return self.config_file["Image"]

    @property
    def volumes(self) -> List[Volume]:
        volume_list = []
        mount_points: dict = self.config_file['MountPoints']
        for mountpoint, config in mount_points.items():
            volume_list.append(Volume(source=config['Source'], destination=mountpoint))
        return volume_list

    def ports_to_string(self) -> str:
        string = ""
        for container_port, host_port_list in self.ports.items():
            if not host_port_list:
                string += "<none>"
            else:
                for mapping in host_port_list:
                    string += f"{mapping['HostIp']}:{mapping['HostPort']}"
            string += "->"
            string += container_port
        return string

    def logging_driver(self) -> str:
        return self.config_file["HostConfig"]["LogConfig"]["Type"]

