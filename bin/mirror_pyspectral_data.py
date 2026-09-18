#!/usr/bin/env python

"""Mirror the pyspectral data files for serving them from a local web location.

Download the relative spectral response and atmospheric correction LUT
tarballs and store them, unextracted, in the directory layout that pyspectral
expects from a mirror. The resulting directory can be copied to a web server,
and pyspectral installations can then be pointed at it with the
``PSP_DATA_BASE_URL`` environment variable instead of downloading from Zenodo.

"""

import argparse
import logging

from pyspectral.utils import AEROSOL_TYPES, logging_off, logging_on, mirror_data

LOG = logging.getLogger(__name__)


def main():
    """Mirror the pyspectral data files."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    parser.add_argument("-o", "--destination", required=True, type=str,
                        help="Directory to write the mirrored files to")
    parser.add_argument("-a", "--aerosol_types", nargs="*", type=str, default=AEROSOL_TYPES,
                        help="Aerosol types to mirror the atmospheric correction LUTs for")
    parser.add_argument("--no_rsr", action="store_true", default=False,
                        help="Do not mirror the relative spectral responses")
    parser.add_argument("--no_luts", action="store_true", default=False,
                        help="Do not mirror the atmospheric correction LUTs")
    parser.add_argument("--source_base_url", type=str, default=None,
                        help=("Base URL to download the files from, for mirroring another mirror. "
                              "Defaults to the upstream locations on Zenodo"))
    parser.add_argument("-f", "--overwrite", action="store_true", default=False,
                        help="Download files even if they are already mirrored")
    parser.add_argument("-d", "--dry_run", action="store_true", default=False,
                        help="Dry run - no action")
    parser.add_argument("-v", "--verbose", action="store_true", help="Turn logging on")

    args = parser.parse_args()

    if args.verbose:
        logging_on(logging.DEBUG)
    else:
        logging_off()

    mirror_data(args.destination,
                aerosol_types=args.aerosol_types,
                include_rsr=not args.no_rsr,
                include_luts=not args.no_luts,
                source_base_url=args.source_base_url,
                overwrite=args.overwrite,
                dry_run=args.dry_run)


if __name__ == "__main__":
    main()
