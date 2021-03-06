from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import *

import casm.vaspwrapper
import sys


def main():
    print("Begin vasp.relax")

    if len(sys.argv) != 2:
        print("Usage: vasp.relax configdir")
        sys.exit()

    configdir = sys.argv[1]

    relaxation = casm.vaspwrapper.Relax(configdir)

    relaxation.submit()

    print("Finish vasp.relax\n\n")


if __name__ == "__main__":
    main()
