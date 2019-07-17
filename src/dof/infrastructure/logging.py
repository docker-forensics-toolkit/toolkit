import sys

from termcolor import colored

trace_enabled = False


def trace(message):
    if trace_enabled:
        print(colored(message, 'blue'))


def info(message):
    print(message)


def warn(message):
    print(f"WARNING: {colored(message, 'yellow')}", file=sys.stderr)


def error(message):
    print(f"ERROR: {colored(message, 'red')}", file=sys.stderr)


def highlight(text: str) -> str:
    return colored(text, color='green', attrs=['bold'])


def disable_stacktrace_on_exceptions(debug):
    if not debug:
        sys.tracebacklimit = 0

