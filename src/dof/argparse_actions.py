import argparse
from pathlib import Path


class ValidatePathAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ValidatePathAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        path = Path(value)
        if not path.exists():
            raise argparse.ArgumentError(None, f"The {self.dest} does not exist: {value}")
        setattr(namespace, self.dest, path)
