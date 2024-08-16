import sys


def err(msg):
    sys.stderr.write("ERROR: " + msg + "\n")


def err_exit(msg=None, tb=None, parser=None, exitcode=1):
    if msg:
        err(msg)
    if tb:
        sys.stderr.write(tb)
    if parser:
        parser.print_help()
    sys.exit(exitcode)
