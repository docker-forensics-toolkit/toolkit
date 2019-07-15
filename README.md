# dof - a docker forensics toolkit
A toolkit for performing post-mortem analysis of Docker runtime environments
based on forensic HDD copies of the docker host system.

## Features

* Mount a forensic image (courtesy of [the imagemounter library](https://github.com/ralphje/imagemounter))
* List Containers and their settings
* Mount a container file system 
* Show container log files
* List Container images
* Inspect build history of container images
* Perform a timeline analysis of the container file system

See [usage.md](USAGE.md) for a tour of the features.

## Development

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
