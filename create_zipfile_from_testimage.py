#!/usr/bin/env python

import argparse
import subprocess
import os
from pathlib import Path

FILES_USED_IN_TEST = [
    "usr/bin/docker",
    "usr/bin/dockerd",
    "var/lib/docker",
]

parser = argparse.ArgumentParser()
parser.add_argument('--image-mountpoint')
args = parser.parse_args()
image_mountpoint = Path(args.image_mountpoint)
if not image_mountpoint.exists():
    raise Exception(f"Image Mountpoint does not exist: {image_mountpoint}")

output_archive = os.path.join(os.getcwd(), "tests", "files_for_integration_test.tgz")
subprocess.run(" ".join(["tar", "-cvzf", output_archive] + FILES_USED_IN_TEST), shell=True,
               check=True, cwd=image_mountpoint)

