# -*- coding: utf-8 -*-
import logging
import argparse

import library.UI as UI
#import library.database as DB

#######################################################################

logging.basicConfig(level=logging.INFO,
                    format='%(name)s - %(levelname)s - %(message)s')

DEBUG=True

#######################################################################

if __name__ == "__main__":

    UI.menu()