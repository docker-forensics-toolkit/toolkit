# A Docker forensics toolkit

This repo contains a toolkit for performing post-mortem analysis of Docker
runtime environments based on forensic HDD copies of the docker host system.

<img alt="Logo" align="right" src="https://avatars2.githubusercontent.com/u/48415084">

![Build Status](https://api.travis-ci.org/docker-forensics-toolkit/toolkit.svg?branch=master)

## Features

* `mount-image` Mounts the forensic image of the docker host
* `status` Prints status information about the container runtime
* `list-images` Prints images found on the computer
* `show-image-history` Displays the build history of an image
* `show-image-config` Pretty prints the full config file of an image
* `list-containers` Prints containers found on the computer
* `show-container-log` Displays the latest container logfiles
* `show-container-config` Pretty prints the combined container specific config files (config.v2.json and hostconfig.json).
* `mount-container`     Mounts the file system of a given container at the given location (overlay2 only)
* `macrobber-container-layer` Extracts file system metadata from the container layer of the given container. Use the output with the 'mactime' tool to create a timeline.
* `macrobber-volumes` Extracts file system metadata from the volumes of the given container. Use the output with the 'mactime' tool to create a timeline.
* `carve-for-deleted-docker-files` Carves the image for deleted Docker files, such as container configs,Dockerfiles and deleted log files. Requires 'scalpel' to be installed.


See [usage.md](USAGE.md) for a tour of the features.

## Development

[git-lfs](https://git-lfs.github.com/) is required to check out this repository. Use whatever editor you like.

## Testing

Testing this tool in integration with a real Docker host image is complicated because:
* Mounting images typically requires root permissions
* Tests need to be executed as root to be able to read files owned by root on
  the Docker Host file system

Therefore there are two ways to test this tool: one with a real docker Host
Image and one with a temporary folder containing select files from a Docker Host
image (created by running the `create_zipfile_from_testimage.py` script. For
local development it's recommended to use the first way while CI may use the
latter.

# Testing with a real Docker Host Image

1. Mount the Docker Host image by running:
    
    sudo python src/dof/main.py mount-image testimages/alpine-host/output-virtualbox-iso/packer-virtualbox-iso-*-disk001.vmdk.raw

Note the mountpoint of the root Partition in the output:
    
    Mounted volume 4.3 GiB 4:Ext4 / [Linux] on /tmp/test-4-root-2.

2. Run the pytest command as root with the image-mountpoint as parameter

    sudo pytest --image-mountpoint=/tmp/test-4-root-2

## Distribution

The toolkit is distributed as a runnable 'fat' binary, bundled with a Python
interpreter. The binary is created by
[PyInstaller](https://www.pyinstaller.org/). To create such a binary run:

    pyinstaller dof.spec
