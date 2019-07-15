import sys

from termcolor import colored


def info(message):
    print(message)


def warn(message):
    print(f"WARNING: {colored(message, 'yellow')}", file=sys.stderr)


def error(message):
    print(f"ERROR: {colored(message, 'red')}", file=sys.stderr)


def highlight(text: str) -> str:
    return colored(text, color='green', attrs=['bold'])
