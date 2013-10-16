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

"""Derive the Near-Infrared reflectance of a given band in the solar and
thermal range (usually the 3.7-3.9 micron band) using a thermal atmospheric
window channel (usually around 11-12 microns).
"""
import logging
LOG = logging.getLogger(__name__)

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy import integrate

from pyspectral.solar import (SolarIrradianceSpectrum, 
                              TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
from pyspectral.blackbody import blackbody


def reflectance(rsr_nir, sunz, tb_nir, tb_therm, solar_flux=None):
    """Given the relative spectral response of the NIR band, the solar zenith
    angle, and the brightness temperatures of the NIR and the Thermal bands,
    derive the solar reflectance for the NIR band removing the thermal
    (terrestrial) part.
    The in-band solar flux over the NIR band is optional. If not provided, it
    will be calculated here!

    The relfectance calculated is without units and should be between 0 and 1.
    """
    # Resample/Interpolate the response curve:
    try:
        wvl = rsr_nir['wavelength']
        resp = rsr_nir['response']
    except KeyError:
        LOG.debug("Calculate for detector = 1")
        wvl = rsr_nir['det-1']['wavelength']
        resp = rsr_nir['det-1']['response']
        
    start = wvl[0]
    end = wvl[-1]
    dlambda = 0.0005
    xspl = np.linspace(start, end, (end-start)/dlambda)

    ius = InterpolatedUnivariateSpline(wvl, resp)
    resp_ipol = ius(xspl)

    wavel = xspl / 1000000.0 # microns -> meters
    b_nir = blackbody(wavel, tb_nir) * resp_ipol
    b_nir_thermal_emiss_one = blackbody(wavel, tb_therm) * resp_ipol
    
    l_nir = integrate.trapz(b_nir, wavel)
    thermal_emiss_one = integrate.trapz(b_nir_thermal_emiss_one, wavel)
    LOG.debug("Radiance: ch3b = ", l_nir)
    LOG.debug("Thermal part assuming ch3b emissivity = 1: ", thermal_emiss_one)

    if not solar_flux:
        solar_spectrum = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, 
                                                 dlambda=0.0005)
        solar_spectrum.read()
        # Calculate the solar-flux:
        solar_flux = solar_spectrum.solar_flux_over_band(rsr_nir)
        LOG.info("Solar flux = " + str(solar_flux))

    nomin = l_nir - thermal_emiss_one
    mu0 = np.cos(np.deg2rad(sunz))
    denom = 1./np.pi * solar_flux * mu0 - thermal_emiss_one

    return nomin / denom
    
