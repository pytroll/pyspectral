#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Adam.Dybbroe

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

"""Test the AHI plugins
"""


#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'

import sys
import logging

LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)

formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                              datefmt=_DEFAULT_TIME_FORMAT)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(handler)


from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.solar import (
    SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
ahi = RelativeSpectralResponse('himawari', '8', 'ahi')
solar_irr = SolarIrradianceSpectrum(
    TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.005)
sflux = solar_irr.inband_solarflux(ahi.rsr['ch7'])
LOG.info("Solar flux over Band: " + str(sflux))

from pyspectral.near_infrared_reflectance import Calculator
sunz = [80., 80.5]
tb7 = [288.0, 290.0]
tb14 = [282.0, 272.0]
tb16 = [275.0, 269.0]
refl38 = Calculator(
    'himawari', '8', 'ahi', 'ch7', detector='det-1', solar_flux=sflux,
    tb2rad_lut_filename='/tmp/ahi_tb2rad_lut.npz')
x = refl38.reflectance_from_tbs(sunz, tb7, tb14)
LOG.info("Reflectance: " + str(x))
y = refl38.reflectance_from_tbs(sunz, tb7, tb14, tb16)
print("Reflectance - co2 corrected: " + str(y))
