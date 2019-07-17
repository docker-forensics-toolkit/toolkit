import subprocess
from pathlib import Path

from decorators import requires_tool
from infrastructure.logging import trace


@requires_tool("scalpel")
def run_carve_for_deleted_docker_files(args):
    scapel_config_file = Path(__file__).resolve().parent.parent / "infrastructure" / "scalpel_docker.conf"
    command = ["scalpel", "-c", str(scapel_config_file), str(args.image_path)]
    trace(f'Running: {" ".join(command)}')
    subprocess.check_call(command)

