"""Plot relative spectral responses for specified sensor(s)."""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from pyspectral.rsr_reader import RelativeSpectralResponse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Plot relative spectral response for a given sensor band')
    parser.add_argument("platform_name", metavar='p',
                        help="The Platform name",
                        type=str)
    parser.add_argument("sensor", metavar='s',
                        help="The sensor/instrument name",
                        type=str)
    parser.add_argument("-r", "--minimum_response",
                        help=("Minimum response: Any response lower than " +
                              "this will be ignored when plotting"),
                        default=0.01, type=float)
    parser.add_argument("-x", "--xlimits", nargs=2,
                        help=("x-axis boundaries for plot"),
                        default=None, type=float)
    parser.add_argument("--title", help=("Plot title"),
                        default=None, type=str)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--wavelength", '-w',
                       help="The wavelength in micrometers", type=float)
    group.add_argument("--bandname", '-b',
                       help="The sensor band name", type=str)

    args = parser.parse_args()

    title = args.title
    if not title:
        title = 'Relative Spectral Responses'

    platform = args.platform_name
    sensor = args.sensor
    minimum_response = args.minimum_response
    xlimits = args.xlimits
    rsr = RelativeSpectralResponse(platform, sensor)

    if args.bandname:
        band = args.bandname
    else:
        wavelength = args.wavelength
        band = rsr.get_bandname_from_wavelength(wavelength)

    detectors = rsr.rsr[band].keys()
    for det in detectors:
        resp = rsr.rsr[band][det]['response']
        wvl = rsr.rsr[band][det]['wavelength']

        resp = np.ma.masked_less_equal(resp, minimum_response)
        wvl = np.ma.masked_array(wvl, resp.mask)
        resp.compressed()
        wvl.compressed()
        plt.plot(wvl, resp)
        if xlimits:
            plt.xlim(xlimits[0], xlimits[1])

    plt.title(title)
    plt.savefig('{}_{}_rsr_band{}.png'.format(platform, sensor, band))
