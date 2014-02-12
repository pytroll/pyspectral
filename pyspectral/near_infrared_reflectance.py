#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Adam.Dybbroe

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

"""Derive the Near-Infrared reflectance of a given band in the solar and
thermal range (usually the 3.7-3.9 micron band) using a thermal atmospheric
window channel (usually around 11-12 microns).
"""
import logging
LOG = logging.getLogger(__name__)

import numpy as np

from pyspectral.solar import (SolarIrradianceSpectrum, 
                              TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)


WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'

EPSILON = 0.01
TB_MIN = 150.
TB_MAX = 360.

from pyspectral.radiance_tb_conversion import Calculator as RadtbConverter

class Calculator(RadtbConverter):
    """A thermal near-infrared (e.g. 3.7 micron) band reflectance calculator.
    
    Given the relative spectral response of the NIR band, the solar zenith
    angle, and the brightness temperatures of the NIR and the Thermal bands,
    derive the solar reflectance for the NIR band removing the thermal
    (terrestrial) part.  The in-band solar flux over the NIR band is
    optional. If not provided, it will be calculated here!

    The relfectance calculated is without units and should be between 0 and 1.
    """
    def __init__(self, platform, satnum, instrument, solar_flux=None, 
                 **options): 
        super(Calculator, self).__init__(platform, satnum, instrument, 
                                         method=1, **options)

        if solar_flux == None:
            self._get_solarflux()
        else:
            self.solar_flux = solar_flux
        self._rad37 = None
        self._rad37_t11 = None
        self._solar_radiance = None
        self._rad39_correction = 1.0


    def derive_rad39_corr(self, bt11, bt13, method='rosenfeld'):
        """Derive the 3.9 radiance correction factor to account for the
        attenuation of the emitted 3.9 radiance by CO2 absorption. Requires the
        11 micron window band and the 13.4 CO2 absorption band, as
        e.g. available on SEVIRI. Currently only supports the Rosenfeld method"""
        if method != 'rosenfeld':
            raise AttributeError("Only CO2 correction for SEVIRI using " + 
                                 "the Rosenfeld equation is supported!")

        LOG.debug("Derive the 3.9 micron radiance CO2 correction coefficent")
        self._rad39_correction = (bt11 - 0.25 * (bt11 - bt13)) ** 4 / bt11 ** 4

    def _get_solarflux(self):
        """Derive the in-band solar flux from rsr over the Near IR band (3.7 or
        3.9 microns)"""
        solar_spectrum = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, 
                                                 dlambda=0.0005)
        self.solar_flux = solar_spectrum.inband_solarflux(self.rsr['IR3.9'])

    def reflectance_from_tbs(self, sunz, tb_nir, tb_therm, 
                             lookuptable=None):
        """
        The relfectance calculated is without units and should be between 0 and 1.
        """
        import os.path

        if np.isscalar(tb_nir):
            tb_nir = np.array([tb_nir, ])
        if np.isscalar(tb_therm):
            tb_therm = np.array([tb_therm, ])

        if tb_therm.shape != tb_nir.shape:
            raise ValueError('Dimensions does not match!' + 
                             str(tb_therm.shape) + ' and ' + str(tb_nir.shape))

        if not self.instrument == 'seviri':
            raise NotImplementedError('Not yey support for other ' + 
                                      'instruments than SEVIRI!')

        thermal_emiss_one = self.tb2radiance_simple('IR10.8', tb_therm)
        l_nir = self.tb2radiance_simple('IR3.9', tb_nir)

        mu0 = np.cos(np.deg2rad(sunz))
        #mu0 = np.where(np.less(mu0, 0.1), 0.1, mu0)
        self._rad37 = l_nir
        self._rad37_t11 = thermal_emiss_one
        self._solar_radiance = 1./np.pi * self.solar_flux * mu0

        # CO2 correction to the 3.9 radiance:
        # self._rad39_correction

        mask = thermal_emiss_one > l_nir

        nomin = l_nir - thermal_emiss_one * self._rad39_correction
        LOG.debug("Shapes: " + str(mu0.shape) + "  " + 
                  str(thermal_emiss_one.shape))
        denom = self._solar_radiance - thermal_emiss_one * self._rad39_correction
        
        retv = nomin / denom
        retv = np.ma.masked_array(retv, mask = mask)
        return np.ma.masked_where(retv < 0, retv)
