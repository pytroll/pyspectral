#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, 2018 Adam.Dybbroe

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

"""Plot relative spectral responses for a list of sensors"""

import argparse
import matplotlib.pyplot as plt
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import get_bandname_from_wavelength
import numpy as np

platforms = ['Himawari-8', 'GOES-16', 'Meteosat-10',
             'EOS-Aqua', 'Sentinel-3A', 'Sentinel-3A',
             'Suomi-NPP', 'NOAA-20']
sensors = ['ahi', 'abi', 'seviri', 'modis', 'olci', 'slstr', 'viirs', 'viirs']


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Plot relative spectral responses for a list of sensors')
    parser.add_argument("wavelength", metavar='w',
                        help="The wavelength in micrometers",
                        type=float)
    parser.add_argument("-t", "--minimum_response",
                        help=("Minimum response: Any response lower than " +
                              "this will be ignored when plotting"),
                        default=0.01, type=float)

    args = parser.parse_args()

    wavelength = args.wavelength
    minimum_response = args.minimum_response

    for platform, sensor in zip(platforms, sensors):
        rsr = RelativeSpectralResponse(platform, sensor)

        band = get_bandname_from_wavelength(sensor, wavelength, rsr.rsr)
        if not band:
            continue

        detectors = rsr.rsr[band].keys()
        # for det in detectors:
        det = detectors[0]
        resp = rsr.rsr[band][det]['response']
        wvl = rsr.rsr[band][det]['wavelength']

        resp = np.ma.masked_less_equal(resp, minimum_response)
        wvl = np.ma.masked_array(wvl, resp.mask)
        resp.compressed()
        wvl.compressed()
        plt.plot(wvl, resp, label=sensor)

    plt.legend()
    plt.savefig('rsr_%s.png' % str(wavelength))
