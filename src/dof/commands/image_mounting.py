from decorators import requires_root, requires_tool
from infrastructure.disk_mounting.imagemounter_lib import mount_all_partitions_in_image


@requires_root
@requires_tool("mount")
def run_mount_image(args):
    mount_all_partitions_in_image(args.image_path)

