import json
from pathlib import Path

from infrastructure.logging import trace


class SwarmConfigLocator:
    def __init__(self, docker_home: Path):
        self.docker_home = docker_home

    def swarm_state_file(self) -> Path:
        return self.docker_home / "swarm" / "state.json"

    @property
    def is_part_of_swarm(self):
        trace(f"Checking for file: {self.swarm_state_file()}")
        return self.swarm_state_file().exists()

    @property
    def node_id(self) -> str:
        trace(f"Reading file: {self.swarm_state_file()}")
        with self.swarm_state_file().open() as file:
            state_file_content = json.load(file)
            return state_file_content[0]['node_id']
