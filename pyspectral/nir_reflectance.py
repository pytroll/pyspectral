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

class Calculator(object):
    """A thermal near-infrared (e.g. 3.7 micron) band reflectance calculator.
    
    Given the relative spectral response of the NIR band, the solar zenith
    angle, and the brightness temperatures of the NIR and the Thermal bands,
    derive the solar reflectance for the NIR band removing the thermal
    (terrestrial) part.  The in-band solar flux over the NIR band is
    optional. If not provided, it will be calculated here!

    The relfectance calculated is without units and should be between 0 and 1.
    """
    def __init__(self, rsr_nir, solar_flux=None):
        """
        Input: 
          rsr_nir = thermal near-infrared band relative spectral response
        Optional:
          solar_flux = In-band solar flux
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

        self.rsr = {'wavelength': wavel, 'response': resp_ipol, 
                    'units': ('m', None)}
        self.rsr_input = rsr_nir

        if solar_flux == None:
            self._get_solarflux()
        else:
            self.solar_flux = solar_flux


    def _get_solarflux(self):
        """Derive the in-band solar flux from rsr"""
        solar_spectrum = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, 
                                                 dlambda=0.0005)
        self.solar_flux = solar_spectrum.solar_flux_over_band(self.rsr_input)

    def tb2radiance(self, tb_):
        """Get the radiance from the brightness temperature (Tb) given the
        thermal near-infrared band spectral response"""
 
        planck = blackbody(self.rsr['wavelength'], tb_) * self.rsr['response']
        return integrate.trapz(planck, (self.rsr['wavelength']))

    def make_tb2rad_lut(self, filepath, resolution=0.1):
        """Generate a Tb to radiance look-up table"""

        tb_ = np.arange(180.0, 360.0, resolution)
        #print "Tb shape = ", tb_.shape
        rad = self.tb2radiance(tb_)
        #print "Radiance shape = ", rad.shape
        
        np.savez(filepath, tb=tb_, radiance=rad.compressed())

    def read_tb2rad_lut(self, filepath):
        """Read the Tb to radiance look-up table"""

        retv = np.load(filepath, 'r')
        return retv

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

        # The following can be done by applying a look-up-table:
        if lookuptable and os.path.exists(lookuptable):
            LOG.info("Using radiance-tb look up table to derive radiances")
            ntb_therm = (tb_therm * 10).astype('int16')
            ntb_nir = (tb_nir * 10).astype('int16')
            lut = self.read_tb2rad_lut(lookuptable)
            start = int(lut['tb'][0] * 10)
            #print "Start tb in lut * 10: ", start
            #dx_ = (lut['tb'][1] - lut['tb'][0]) * 10
            thermal_emiss_one = lut['radiance'][ntb_therm - start]
            l_nir = lut['radiance'][ntb_nir - start]
        else:
            thermal_emiss_one = self.tb2radiance(tb_therm)
            l_nir = self.tb2radiance(tb_nir)

        #print thermal_emiss_one.min(), thermal_emiss_one.max()
        #print l_nir.min(), l_nir.max()

        nomin = l_nir - thermal_emiss_one
        mu0 = np.cos(np.deg2rad(sunz))
        LOG.debug("Shapes: " + str(mu0.shape) + "  " + str(thermal_emiss_one.shape))
        denom = 1./np.pi * self.solar_flux * mu0 - thermal_emiss_one
        
        retv = np.where(np.greater(abs(denom), 0.00001), nomin / denom, -9)
        return np.ma.masked_array(retv, mask = retv < 0)
