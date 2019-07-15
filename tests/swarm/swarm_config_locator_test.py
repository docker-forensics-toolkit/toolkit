from pathlib import Path

from infrastructure.swarm_config_locator import SwarmConfigLocator

path_with_test_files = Path(__file__).resolve().parent.parent


def test_swarm_config_file_locator():
    config_locator = SwarmConfigLocator(path_with_test_files)
    assert config_locator.is_part_of_swarm
    assert config_locator.node_id == "7pnvo1rle72mkhjmsbm40bxga"
