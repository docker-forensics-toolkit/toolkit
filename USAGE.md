# How to use the Docker Forensics Toolkit

## Usage scenario

You have been handed a forensic HDD copy or disk image of a Docker host system. It's your task to find out what
happend to the system. Let's dig in.

## Mounting the image

First you need to mount the container hosts filesystem. You can use any tool to do this, our use the built-in 
`mount-image` command:
    
    >> sudo dof mount-image testimages/alpine-host/output-virtualbox-iso/packer-virtualbox-iso-1561712912-disk001.raw
    
The output will look like this:

      Mounted volume 100.0 MiB 2:Ext4 /mnt/boot [Linux] at path /tmp/packer-virtualbox-iso-1561712912-disk001-2-mnt_boot-2.
      Unsupported filesystem 3:Linux Swap / Solaris x86 (0x82) (type: swap, block offset: 206848, length: 3072000)
      Execution failed due to <class 'imagemounter.exceptions.UnsupportedFilesystemError'> swap
      Traceback (most recent call last):
      imagemounter.exceptions.UnsupportedFilesystemError: swap
      WARNING: Exception while mounting swap volume 1.46 GiB 3:Linux Swap / Solaris x86 (0x82)
      Mounted volume 4.3 GiB 4:Ext4 / [Linux] at path /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2.
    
We have now mounted the Docker Hosts root folder. Let's take a deeper look at 
the mountpoint `/tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2`.

## Orientation

You may not know much about the Docker Host environment. So let's first get a quick overview of what's going on in this 
machine.

    dof status /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2
    
The output will look like this: 

    TODO: insert output
    
## Containers

Now let's take a closer look at some of these containers that were running when the image was created.

    dof list-containers /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2

The output will look like this:

    /apache
    	ID: 25b0a6f529c117ffc47684b4749f3ef38c1d9b2dce5a1cd52513e05af9d11522
    	State: running
    	Created: 2019-06-28T11:11:08.347278022Z
    	Image: httpd:2.4.38-alpine
    	Image ID: sha256:0c388cccfd046fb7f46560e6605e128f0bd0c2bb2f5858b84b0f16d1497e32a6
    	Entrypoint: None
    	Storage Driver: overlay2
    	Container Layer: /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2/var/lib/docker/overlay2/ab3480793a4d06555b3e7ac8f3ffef584bb3b3bdbffbc6e7e7e863768f849fa4/diff
    	Ports: {'80/tcp': None}
    
    /mysql
    	ID: c155196e5689cb7dd57f52ca9efeadc3d2d0be14e73245497909ba4c73f16f3f
    	State: dead
    	Created: 2019-06-28T11:11:28.802084249Z
    	Image: mysql:8.0.16
    	Image ID: sha256:c7109f74d339896c8e1a7526224f10a3197e7baf674ff03acbab387aa027882a
    	Entrypoint: ['docker-entrypoint.sh']
    	Storage Driver: overlay2
    	Container Layer: /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2/var/lib/docker/overlay2/2f583c9efac3388f02acd4d8d30a271a805346dc0d8dd17613eab567d032b857/diff
    	Ports: <none>
    	Volume: Host folder '/var/mysql/datadir' mounted in in Container at '/var/lib/mysql'

There's the one running container and the one that's dead. We also see more info about both containers. Let's inspect
the apache container closer. Feel free to ignore the `/` in the container name, it's an artifact of the way Docker
persists the container names.


## Image build history

Sometimes there may be a malicious image involved in an incident. Fortunately Docker keeps a log of all the images'
build history. Let's take a look at how a particular image was built:

    sudo python dof show-image-history --image httpd:2.4.38-alpine /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2

The output will look like this:

    [{'created': '2019-03-07T22:19:40.113750514Z',
      'created_by': '/bin/sh -c #(nop) ADD '
                    'file:88875982b0512a9d0ba001bfea19497ae9a9442c257b19c61bffc56e7201b0c3 '
                    'in / '},
    [...output truncated for readability...]
    {'created': '2019-03-07T23:16:29.086340385Z',
     'created_by': '/bin/sh -c #(nop) COPY '
                   'file:8b68ac010cb13f58ebe31c3015d15c988625d2fde7339dca8a84c3c914493323 '
                   'in /usr/local/bin/ '},
    {'created': '2019-03-07T23:16:29.291065206Z',
     'created_by': '/bin/sh -c #(nop)  EXPOSE 80',
     'empty_layer': True},
    {'created': '2019-03-07T23:16:29.459280565Z',
     'created_by': '/bin/sh -c #(nop)  CMD ["httpd-foreground"]',
     'empty_layer': True}]

    
## Container logs

To inspect the logfiles of the `apache` container processes run:

    dof show-container-log --container apache /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2
  
The output will look like this:

    {"log":"AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using 172.17.0.2. Set the 'ServerName' directive globally to suppress this message\n","stream":"stderr","time":"2019-06-28T11:11:08.885229622Z"}
    {"log":"AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using 172.17.0.2. Set the 'ServerName' directive globally to suppress this message\n","stream":"stderr","time":"2019-06-28T11:11:08.886654245Z"}
    {"log":"[Fri Jun 28 11:11:08.889950 2019] [mpm_event:notice] [pid 1:tid 139817734703976] AH00489: Apache/2.4.38 (Unix) configured -- resuming normal operations\n","stream":"stderr","time":"2019-06-28T11:11:08.890039115Z"}
    {"log":"[Fri Jun 28 11:11:08.891651 2019] [core:notice] [pid 1:tid 139817734703976] AH00094: Command line: 'httpd -D FOREGROUND'\n","stream":"stderr","time":"2019-06-28T11:11:08.891696185Z"}


## Timeline analysis 

Let's say we narrowed our search down to one or more containers. Let's look at the filesystem activity, to get a feeling 
for what happend in this container. Since the docker file system is read only, except for the container layer (a unique
file system layer on top of the image for each container instance) and the mounted volumes, we analyse these two places
and combine the output to pipe it into the `mactime` utility that's part of The Sleuth Kit (TSK).

    { sudo dof macrobber-container-layer --container mysql /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2 & sudo dof macrobber-volumes --container mysql /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2 ; } | mactime 2019-01-01..2019-12-31    

The output will look like this:

    Tue Jun 11 2019 01:45:11     4096 m... drwxr-xr-x 0        0        140527   /run
    Fri Jun 28 2019 13:11:29     4096 .a.. drwxr-xr-x 0        0        140527   /run
                                 4096 .a.. drwxrwxrwx 999      999      140528   /run/mysqld
    Fri Jun 28 2019 13:11:39     4096 mac. drwxrwxrwt 0        0        140521   /tmp
                                 4096 ..c. drwxr-xr-x 0        0        140527   /run
                                 4096 m.c. drwxrwxrwx 999      999      140528   /run/mysqld
                                    3 mac. -rw------- 999      999      140529   /run/mysqld/mysqld.sock.lock
                                    0 mac. srwxrwxrwx 999      999      140530   /run/mysqld/mysqld.sock
                                    3 mac. -rw-r----- 999      999      140531   /run/mysqld/mysqld.pid
                                    4 mac. -rw------- 999      999      140532   /run/mysqld/mysqlx.sock.lock
                                    0 mac. srwxrwxrwx 999      999      140533   /run/mysqld/mysqlx.sock
    Sat Jun 29 2019 14:10:39     4098 mac. drwxrwxrwt 0        0        140521   /tmp/trojan

Looks like someone created a file named `trojan` on June 29th at 14:10:39 at `/tmp/trojan`. Let's take a closer look.

## Mounting the container filesystem 

To get a copy of the file and poke around the container file system it's nice to see a unified view of the file system 
layers. To do so, let's mount the container file system next:

    sudo dof mount-container --container apache /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2
    
The output is short:
    
    Mounted container apache at /tmp/tmpgq68ywnl
    
Let's take a closer look:

    » ls /tmp/tmpgq68ywnl
    bin/  dev/  etc/  home/  lib/  media/  mnt/  opt/  proc/  root/  run/  sbin/  srv/  sys/  tmp/  usr/  var/

Nice. Now we can inspect the suspect file and poke around some more. 

## Images

You can inspect all the images on a Docker host as follows:

    sudo dof list-images /tmp/packer-virtualbox-iso-1561712912-disk001-4-root-2

The output will look like this:

    Images in Repository: <none>
        Id: 881787037d6fd84c779a6ef2d6ad58237ecd90e85714b7c375a2bab1d429d76a
        Tags: <none>
        Containers: <none>

    Images in Repository: httpd
        Id: 0c388cccfd046fb7f46560e6605e128f0bd0c2bb2f5858b84b0f16d1497e32a6
        Tags: httpd:2.4.38-alpine, httpd@sha256:eb8ccf084cf3e80eece1add239effefd171eb39adbc154d33c14260d905d4060
        Containers: /apache


    Images in Repository: mysql
        Id: c7109f74d339896c8e1a7526224f10a3197e7baf674ff03acbab387aa027882a
        Tags: mysql:8.0.16, mysql@sha256:415ac63da0ae6725d5aefc9669a1c02f39a00c574fdbc478dfd08db1e97c8f1b
        Containers: /mysql
   
Images that don't belong to a Repository were not pulled from Docker Hub or a private Registry, but likely built on this 
machine. They deserve some extra scrutiny. 

Images without a corresponding container instance may indicate a deleted container.

