from pathlib import Path
from typing import List

from imagemounter import ImageParser, Volume

from infrastructure.logging import warn, info, error, highlight


def mount_all_partitions_in_image(image_path: Path) -> List[Volume]:
    """
    Uses the imagemounter python library to mount the forensic image for further analysis.

    Adapted from https://github.com/ralphje/imagemounter/blob/master/examples/simple_cli.py
    """
    parser = ImageParser([image_path], pretty=True)
    mounted_volumes = []
    for volume in parser.init():
        if volume.mountpoint:
            # If the mountpoint is set, we have successfully mounted it
            info(f"Mounted volume {highlight(volume.get_description())} "
                 f"at path {highlight(volume.mountpoint)}.")
            mounted_volumes.append(volume)
        elif volume.loopback:
            # If the mountpoint is not set, but a loopback is used, this is probably something like an LVM that did
            # not work properly.
            info(f"Mounted volume {highlight(volume.get_description())} as loopback on {highlight(volume.loopback)}.")
        elif volume.exception and volume.fstype == "swap":
            warn(f"Exception while mounting swap volume {volume.get_description()}")
        elif volume.exception:
            # Other exceptions are a bit troubling. Should never happen, actually.
            error(f"Exception while mounting {volume.get_description()}")
    return mounted_volumes

