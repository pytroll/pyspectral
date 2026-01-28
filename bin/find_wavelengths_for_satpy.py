"""Retrieve channel wavelength ranges for a given sensor."""

import argparse

from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import get_wave_range


def _setup_argparse():
    arg_parser = argparse.ArgumentParser(
        description='Retrieve channel wavelength ranges for a given sensor.')
    arg_parser.add_argument("platform_name",
                            help="The Platform name",
                            type=str)
    arg_parser.add_argument("sensor",
                            help="The sensor/instrument name",
                            type=str)
    arg_parser.add_argument("-r", "--minimum_response",
                            help=("Minimum response threshold: Defines the value "
                                  "that the RSR must exceed in order to trigger"
                                  "the minimum or maximum wavelengths."),
                            default=0.15, type=float)
    arg_parser.add_argument("--bandname", '-b',
                            help="The sensor band name. Leave blank to return all bands.", type=str)
    arg_parser.add_argument("--detector", '-d',
                            help="The sensor detector, if not passed will default to det-1",
                            default='det-1', type=str)
    return arg_parser


def main(arguments):
    """Retrieve wavelength range based on user-supplied arguments."""
    platform = arguments.platform_name
    sensor = arguments.sensor
    threshold = arguments.minimum_response

    rsr = RelativeSpectralResponse(platform, sensor)
    if arguments.bandname:
        bands = [arguments.bandname]
    else:
        bands = rsr.band_names
    det = arguments.detector

    for bname in bands:
        wvls = get_wave_range(rsr.rsr[bname][det], threshold)
        print(f'name:  {bname}')
        print(f'  wavelength: [{wvls[0]:5.3f}, {wvls[1]:5.3f}, {wvls[2]:5.3f}]')


if __name__ == "__main__":

    parser = _setup_argparse()
    args = parser.parse_args()
    main(args)
