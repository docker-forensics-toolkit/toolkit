import argparse
import os
import subprocess
from pathlib import Path

from infrastructure.logging import warn, error


def requires_root(fun):
    """Commands annotated with this decorator usually require root privilleges.
       This decorator outputs a warning about this to the user."""

    def root_warning_wrapper(*args, **kwargs):
        if os.geteuid() != 0:
            warn("You may need root privileges to do this, but it doesn't look like you are root. "
                 "Try running this command with sudo, if it fails.")
        fun(*args, **kwargs)

    return root_warning_wrapper


def requires_docker_home_argument(fun):
    """Commands annotated with this decorator usually use the docker home directory, so
       they will get the docker_home argument passed as a parameter automatically."""

    def requires_docker_home_argument_wrapper(*args, **kwargs):
        argparse_args = args[0]
        image_mountpoint: Path = argparse_args.image_mountpoint
        docker_home = image_mountpoint / argparse_args.docker_home
        if not docker_home.exists():
            raise argparse.ArgumentError(None, f"The docker_home path does not exist: {docker_home}")
        fun(*args, image_mountpoint=image_mountpoint, docker_home=docker_home)

    return requires_docker_home_argument_wrapper


class requires_tool:
    """Commands annotated with this decorator require a certain tool to be installed."""
    def __init__(self, tool):
        self.tool = tool

    def __call__(self, fun):
        def requires_tool_wrapper(*args, **kwargs):
            try:
                subprocess.check_call(["which", self.tool])
            except subprocess.CalledProcessError as e:
                error(f"This command requires the tool '{self.tool}' to be installed, but it could not be found.")
                exit(1)
            fun(*args, **kwargs)

        return requires_tool_wrapper
