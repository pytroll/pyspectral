#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, 2019 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Script to download the RSR files from internet
"""

import logging
import argparse
from pyspectral.utils import logging_on, logging_off
from pyspectral.rsr_reader import check_and_download

LOG = logging.getLogger(__name__)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Download relative spectral response data in hdf5')
    parser.add_argument("-o", "--destination", help=("Destination path where to store the files"),
                        default=None, type=str)
    parser.add_argument(
        "-d", '--dry_run', help=("Dry run - no action"), action='store_true',
        default=False)
    parser.add_argument(
        "-v", '--verbose', help=("Turn logging on"), action='store_true')

    args = parser.parse_args()
    dest_dir = args.destination
    verbose = args.verbose
    dry_run = args.dry_run

    if verbose:
        logging_on(logging.DEBUG)
    else:
        logging_off()

    if dest_dir:
        check_and_download(dest_dir=dest_dir, dry_run=dry_run)
    else:
        check_and_download(dry_run=dry_run)
