from pathlib import Path
from stat import filemode
from typing import List


def mac_robber_folder(folder: Path, bind_mount_path="") -> List[str]:
    """Extracts file system attributes and timestamps from a file system subtree. You can pipe this output directly
       into the 'mactimes' tool that's part of the Sleuth Kit (https://www.sleuthkit.org/) to create a timeline.

       When a bind_mont_path is given, it will be used as a prefix for the file, to
       reflect the point in the container where the Volume would be mounted.
       When no bind_mount_path is given, the path is absolute to the container's file system."""
    mac_data = []
    for path in folder.glob("**/*"):
        stat = path.lstat()
        dummy = "0"  # dummy value, we don't really care for the md5 and crtime is not available through the Python API

        name = _determine_full_path_in_container(bind_mount_path, folder, path)
        mode = filemode(stat.st_mode)

        # Format expected by TSK. See also:
        # https://github.com/sleuthkit/sleuthkit/blob/9e4bc4b5c0d34dcb266191558337be1e199af3da/tsk/fs/ils_lib.c#L106
        mac_data.append(f"{dummy}|{name}|{stat.st_ino}|{mode}|{stat.st_uid}|{stat.st_gid}|{stat.st_size}|"
                        f"{round(stat.st_atime)}|{round(stat.st_mtime)}|{round(stat.st_ctime)}|{dummy}")
    return mac_data


def _determine_full_path_in_container(bind_mount_path, image_mountpoint,
                                      path_absolute_to_mountpoint):
    relative_path: Path = path_absolute_to_mountpoint.relative_to(image_mountpoint)
    if bind_mount_path:
        absolute_path_in_container = Path(bind_mount_path) / relative_path
    else:
        absolute_path_in_container = Path("/") / relative_path
    if absolute_path_in_container.is_symlink():
        name = str(absolute_path_in_container) + " -> " \
               + str(path_absolute_to_mountpoint.resolve())
    else:
        name = str(absolute_path_in_container)
    return name
