# -*- coding: utf-8 -*-
import logging
import argparse

import library.UI as UI

#######################################################################

logging.basicConfig(level=logging.WARNING,
                    format='%(name)s - %(levelname)s - %(message)s')

DEBUG=True

#######################################################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--chromium', help='Specify a chromium browser,' \
        + ' different from regular Chrome')
    args = parser.parse_args()

    if args.chromium:
        UI.CHROMIUM_PATH = args.chromium
    else:
        UI.CHROMIUM_PATH = None

    UI.menu()