"""Eudoxys utilities"""

import sys
import importlib.metadata as meta

from .cmdline import CommandLine

def main(*args,**kwargs):
    """Eudoxys utilities command line"""

    cmdline = CommandLine()

    print("Eudoxys",__name__,"version",meta.version(__name__))

if __name__ == "__main__":

    sys.exit(main())