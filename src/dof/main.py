import argparse
import os
from pathlib import Path

import argcomplete
import sys

from arguments import ValidatePathAction
from commands.carve_for_deleted_docker_files import run_carve_for_deleted_docker_files
from commands.dump_container_config import run_dump_container_config
from commands.macrobber_container_layer import run_macrobber_container_layer
from commands.container_filesystem_mounting import run_mount_container_command
from commands.image_mounting import run_mount_image
from commands.list_containers import run_list_containers
from commands.list_images import run_list_images
from commands.docker_host_status import run_status_command
from commands.macrobber_volumes import run_macrobber_on_volumes
from commands.show_container_logs import show_container_logfile
from commands.show_image_config import run_show_image_config
from commands.show_image_history import run_show_image_history

__version__ = "0.2.0"


def select_command_and_run():
    disable_stacktrace_on_exceptions_unless_debug_argument_is_set(debug=False)
    parser = argparse.ArgumentParser(description='Toolkit for the forensic post-mortem analysis of Docker host systems')
    parser.add_argument("-V", "--version",
                        action='version',
                        help="Print version number and exit",
                        version=f"%(prog)s v{__version__}")
    subparsers = parser.add_subparsers(title="operation",
                                       description="one of the following operations",
                                       help="start with <operation> help for more info about an operation")
    add_subparsers(subparsers)
    args = parser.parse_args()
    argcomplete.autocomplete(parser)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


def add_subparsers(subparsers):
    add_mount_image_command(subparsers)
    add_status_command(subparsers)
    add_list_images_command(subparsers)
    add_show_image_history_command(subparsers)
    add_show_image_config_command(subparsers)
    add_list_containers_command(subparsers)
    add_show_container_logfile_command(subparsers)
    add_dump_container_config_command(subparsers)
    add_mount_container_command(subparsers)
    add_macrobber_container_layer(subparsers)
    add_macrobber_volumes(subparsers)
    add_carve_for_deleted_docker_files(subparsers)


def add_mount_image_command(subparsers):
    parser = subparsers.add_parser("mount-image",
                                   help="Mounts the forensic image of the docker host")
    parser.add_argument("image_path",
                        action=ValidatePathAction,
                        help="Path of the forensic image")
    parser.set_defaults(func=run_mount_image)


def add_mount_container_command(subparsers):
    parser = subparsers.add_parser("mount-container",
                                   help="Mounts the file system of a given container at the given location.")
    add_docker_home_and_mount_path_parameters(parser)
    parser.add_argument("--at-mountpoint",
                        action=ValidatePathAction,
                        dest="container_mountpoint",
                        help="Path where the container filesystem should be mounted. Must be an existing directory!")
    parser.add_argument("--container",
                        dest="container_name_or_id",
                        help="Name or id of the container",
                        required=True)
    parser.set_defaults(func=run_mount_container_command)


def add_status_command(subparsers):
    parser = subparsers.add_parser("status",
                                   help="Prints status information about the container runtime")
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_status_command)


def add_list_images_command(subparsers):
    parser = subparsers.add_parser("list-images",
                                   help="Prints images found on the computer")
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_list_images)


def add_dump_container_config_command(subparsers):
    parser = subparsers.add_parser("show-container-config",
                                   help="Pretty prints the combined container specific config files "
                                        "(config.v2.json and hostconfig.json).")
    parser.add_argument("--container",
                        dest="container_name_or_id",
                        help="Name or id of the container",
                        required=True)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_dump_container_config)


def add_list_containers_command(subparsers):
    parser = subparsers.add_parser("list-containers",
                                   help="Prints containers found on the computer")
    parser.add_argument("--style",
                        dest="style",
                        choices=["tabular", "linear"],
                        help="Determines the style of the output. Can be 'tabular' or 'linear'",
                        required=False)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_list_containers)


def add_show_image_history_command(subparsers):
    parser = subparsers.add_parser("show-image-history",
                                   help="Displays the build history of an image")
    parser.add_argument("--image",
                        dest="image_tag_or_id",
                        help="Tag or id of the image",
                        required=True)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_show_image_history)


def add_show_image_config_command(subparsers):
    parser = subparsers.add_parser("show-image-config",
                                   help="Pretty prints the full config file of an image")
    parser.add_argument("--image",
                        dest="image_tag_or_id",
                        help="Tag or id of the image",
                        required=True)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_show_image_config)

def add_show_container_logfile_command(subparsers):
    parser = subparsers.add_parser("show-container-log",
                                   help="Displays the latest container logfiles")
    parser.add_argument("--container",
                        dest="container_name_or_id",
                        help="Name or id of the container",
                        required=True)
    parser.add_argument("--editor",
                        dest="editor",
                        help="The editor to launch",
                        required=False)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=show_container_logfile)


def add_macrobber_container_layer(subparsers):
    parser = subparsers.add_parser("macrobber-container-layer",
                                   help="Extracts file system metadata form the container layer of the given container"
                                        "Use the output with the 'mactime' tool to create a timeline.")
    parser.add_argument("--container",
                        dest="container_name_or_id",
                        help="Name or id of the container",
                        required=True)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_macrobber_container_layer)


def add_macrobber_volumes(subparsers):
    parser = subparsers.add_parser("macrobber-volumes",
                                   help="Extracts file system metadata form the volumes of the given container"
                                        "Use the output with the 'mactime' tool to create a timeline.")
    parser.add_argument("--container",
                        dest="container_name_or_id",
                        help="Name or id of the container",
                        required=True)
    add_docker_home_and_mount_path_parameters(parser)
    parser.set_defaults(func=run_macrobber_on_volumes)


def add_docker_home_and_mount_path_parameters(parser):
    environment_variable = os.environ.get("DOF_IMAGE_MOUNTPOINT", None)
    if environment_variable:
        docker_home = os.environ.get("DOF_DOCKER_HOME", None)
        parser.set_defaults(image_mountpoint=Path(environment_variable))
        parser.set_defaults(docker_home=Path("var/lib/docker") or Path(docker_home))
    else:
        parser.add_argument("image_mountpoint",
                            action=ValidatePathAction,
                            default=os.environ.get('DOF_IMAGE_MOUNTPOINT', None),
                            help="The path where the forensic image was mounted."
                                 "the tool assumes /var/lib/docker/ is the docker home directory. "
                                 "Use the docker_home parameter if this is not the case.")
        parser.add_argument("--docker_home",
                            default="var/lib/docker",
                            help="The path to the docker home folder (usually /var/lib/docker)", required=False)


def add_carve_for_deleted_docker_files(subparsers):
    parser = subparsers.add_parser("carve-for-deleted-docker-files",
                                   help="Carves the image for deleted Docker files, such as container configs,"
                                        "Dockerfiles and deleted log files. Requires 'scalpel' to be installed.")
    parser.add_argument("image_path",
                        action=ValidatePathAction,
                        help="Path of the forensic image")
    parser.set_defaults(func=run_carve_for_deleted_docker_files)


def disable_stacktrace_on_exceptions_unless_debug_argument_is_set(debug):
    if not debug:
        sys.tracebacklimit = 0


if __name__ == "__main__":
    select_command_and_run()
