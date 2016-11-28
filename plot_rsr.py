#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, 2016 Adam.Dybbroe@smhi.se

# Author(s):

#   Adam.Dybbroe@smhi.se <a000680@c20671.ad.smhi.se>

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

import matplotlib.pyplot as plt
from pyspectral.rsr_reader import RelativeSpectralResponse

import numpy as np

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: %s <platform_name> <sensor> <band name>" %
              (sys.argv[0]))
        exit(0)

    platform = str(sys.argv[1])
    sensor = str(sys.argv[2])
    band = str(sys.argv[3])

    rsr = RelativeSpectralResponse(platform, sensor)

    detectors = rsr.rsr[band].keys()
    for det in detectors:
        resp = rsr.rsr[band][det]['response']
        wvl = rsr.rsr[band][det]['wavelength']

        resp = np.ma.masked_less_equal(resp, 0.01)
        wvl = np.ma.masked_array(wvl, resp.mask)
        resp.compressed()
        wvl.compressed()
        plt.plot(wvl, resp)

    plt.savefig('%s_%s_rsr_band%s.png' % (platform,
                                          sensor, band))
