#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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

"""Example code to derive the in-band solar flux
"""

from pyspectral.rsr_read import RelativeSpectralResponse
from pyspectral.solar import (SolarIrradianceSpectrum, 
                              TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)

# ---------------------------------------------------------------------------
if __name__ == '__main__':

    this = RelativeSpectralResponse('eos', 2, 'modis')
    this.read(channel='20', scale=0.001)

    that = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, 
                                   dlambda=0.005)
    that.read()

    # Calculate the solar-flux:
    sflux = that.solar_flux_over_band(this.rsr)
    print("Solar flux over Band: ", sflux)

    # import matplotlib.pyplot as plt

    # ax = plt.subplot(111)
    # plt.title('Relative Spectral Response Curve')
    # plt.plot(w_ch, resp_ch, 'o-', color='blue')
    # plt.plot(xspl, resp_ipol, 'o-', color='red')
    # plt.legend(('Original data', 'Interpolation'),
    #            'lower left', shadow=True, fancybox=True)
    # plt.savefig('./rsr_spline_test.png')
