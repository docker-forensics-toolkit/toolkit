import subprocess
from pathlib import Path

from decorators import requires_tool


@requires_tool("scalpel")
def run_carve_for_deleted_docker_files(args):
    image_path = args.image_path
    scapel_config_file = Path(__file__).resolve().parent.parent / "infrastructure" / "scalpel_docker.conf"
    subprocess.check_call(["scalpel", "-c", scapel_config_file, args.image_path])

