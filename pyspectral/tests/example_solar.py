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
import logging
import sys
from pyspectral.rsr_read import RelativeSpectralResponse
from pyspectral.solar import (SolarIrradianceSpectrum, 
                              TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'

# ---------------------------------------------------------------------------

def main():
    """Main"""
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(logging.DEBUG)

    modis = RelativeSpectralResponse('EOS-Aqua', 'modis')
    modis.read(channel='20', scale=0.001)

    solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, 
                                        dlambda=0.005)
    solar_irr.read()

    # Calculate the solar-flux:
    sflux = solar_irr.solar_flux_over_band(modis.rsr)
    print("Solar flux over Band: ", sflux)

    from pyspectral.nir_reflectance import Calculator
    #refl37 = Calculator(modis.rsr, solar_flux=sflux)
    refl37 = Calculator(modis.rsr)

    sunz = 80.
    tb3 = 290
    tb4 = 282
    refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
    print refl

    refl37.make_tb2rad_lut('./modis_EOS-Aqua_band20_tb2rad_lut.npz')

    # import matplotlib.pyplot as plt

    # ax = plt.subplot(111)
    # plt.title('Relative Spectral Response Curve')
    # plt.plot(w_ch, resp_ch, 'o-', color='blue')
    # plt.plot(xspl, resp_ipol, 'o-', color='red')
    # plt.legend(('Original data', 'Interpolation'),
    #            'lower left', shadow=True, fancybox=True)
    # plt.savefig('./rsr_spline_test.png')

if __name__ == '__main__':

    LOG = logging.getLogger('example')

    main()
