from pathlib import Path
from pprint import pprint

from decorators import requires_root, requires_docker_home_argument
from infrastructure.image_locator import ImageLocator


@requires_root
@requires_docker_home_argument
def run_show_image_config(args, image_mountpoint: Path, docker_home: Path):
    image_locator = ImageLocator(docker_home)

    image = image_locator.image_by_tag_or_id(args.image_tag_or_id)

    pprint(image.config_file)




