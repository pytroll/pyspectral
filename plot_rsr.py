#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2018 Adam.Dybbroe@smhi.se

# Author(s):

#   Adam.Dybbroe@smhi.se <adam.dybbroe@smhi.se>

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

"""Plot some spectral responses
"""

import argparse
import matplotlib.pyplot as plt
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import get_bandname_from_wavelength

import numpy as np

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
        band = get_bandname_from_wavelength(sensor, wavelength, rsr.rsr)

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
