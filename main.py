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

    UI.menu()