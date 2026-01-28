"""Download the atmospheric corrections Look-Up Tables.

Script to download the the LUT files for atmospheric correction in the Short
Wave spectral range.

"""

import argparse
import logging

from pyspectral.rayleigh import check_and_download
from pyspectral.utils import AEROSOL_TYPES, logging_off, logging_on

LOG = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download the atm correction LUT files')
    parser.add_argument("--aerosol_types", '-a', nargs='*',
                        help="Aerosol types",
                        type=str, default=AEROSOL_TYPES)
    parser.add_argument(
        "-d", '--dry_run', help=("Dry run - no action"), action='store_true',
        default=False)
    parser.add_argument(
        "-v", '--verbose', help=("Turn logging on"), action='store_true')

    args = parser.parse_args()
    verbose = args.verbose
    dry_run = args.dry_run
    aerosol_types = args.aerosol_types

    if verbose:
        logging_on(logging.DEBUG)
    else:
        logging_off()

    check_and_download(aerosol_types=aerosol_types, dry_run=dry_run)
