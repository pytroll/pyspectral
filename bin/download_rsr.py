"""Script to download the RSR data from internet."""

import argparse
import logging

from pyspectral.rsr_reader import check_and_download
from pyspectral.utils import logging_off, logging_on

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
