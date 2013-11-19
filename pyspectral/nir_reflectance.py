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
from pyspectral.blackbody import blackbody, blackbody_wn

WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'

EPSILON = 0.01
TB_MIN = 180.
TB_MAX = 360.

class Calculator(object):
    """A thermal near-infrared (e.g. 3.7 micron) band reflectance calculator.
    
    Given the relative spectral response of the NIR band, the solar zenith
    angle, and the brightness temperatures of the NIR and the Thermal bands,
    derive the solar reflectance for the NIR band removing the thermal
    (terrestrial) part.  The in-band solar flux over the NIR band is
    optional. If not provided, it will be calculated here!

    The relfectance calculated is without units and should be between 0 and 1.
    """
    def __init__(self, rsr_nir, solar_flux=None, **options):
        """
        Input: 
          rsr_nir = thermal near-infrared band relative spectral response in
          wavelength space (micro meters)
        Optional:
          solar_flux = In-band solar flux
        """
        if 'wavespace' in options:
            if options['wavespace'] not in [WAVE_LENGTH, WAVE_NUMBER]:
                raise AttributeError('Wave space not %s or %s!' % (WAVE_LENGTH, 
                                                                   WAVE_NUMBER))
            self.wavespace = options['wavespace']
        else:
            self.wavespace = WAVE_LENGTH
        if 'tb_resolution' in options:
            self.tb_resolution = options['tb_resolution']
        else:
            self.tb_resolution = 0.1
        self.tb_scale = 1./self.tb_resolution

        # Resample/Interpolate the response curve:
        try:
            wvl = rsr_nir['wavelength']
            resp = rsr_nir['response']
        except KeyError:
            LOG.debug("Calculate for detector = 1")
            wvl = rsr_nir['det-1']['wavelength']
            resp = rsr_nir['det-1']['response']
        
        # Conversion from wavelengths to wave numbers:
        if self.wavespace == WAVE_NUMBER:
            wvl = 1./wvl[::-1] 
            resp = resp[::-1]
            scale = 1000000.0
            unit = 'm-1'
        elif self.wavespace == WAVE_LENGTH:
            scale = 1./1000000.0 # microns -> meters
            unit = 'm'
        else:
            raise AttributeError('wavespace ' + self.wavespace + 
                                 ' not supported!')

        wvl = wvl * scale
        start = wvl[0]
        end = wvl[-1]
        dlambda = (end - start) / 3000.

        xspl = np.linspace(start, end, (end-start)/dlambda)
        ius = InterpolatedUnivariateSpline(wvl, resp)
        resp_ipol = ius(xspl)
        wavel = xspl

        self.rsr = {self.wavespace: wavel, 'response': resp_ipol, 
                    'units': (unit, None)}
        self.rsr_integral = np.trapz(resp_ipol, wavel)
        #print("RSR integral: " + str(self.rsr_integral))

        self.rsr_input = rsr_nir

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
        """Derive the in-band solar flux from rsr"""
        solar_spectrum = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, 
                                                 dlambda=0.0005)
        self.solar_flux = solar_spectrum.inband_solarflux(self.rsr_input)

    def tb2radiance(self, tb_, lut=False):
        """Get the radiance from the brightness temperature (Tb) given the
        thermal near-infrared band spectral response"""
 
        if lut:
            ntb = (tb_ * self.tb_scale).astype('int16')
            start = int(lut['tb'][0] * self.tb_scale)
            return lut['radiance'][ntb - start]
            
        if self.wavespace == WAVE_LENGTH:
            planck = (blackbody(self.rsr['wavelength'], tb_) * 
                      self.rsr['response'])
        else:
            planck = (blackbody_wn(self.rsr[self.wavespace], tb_) * 
                      self.rsr['response'])

        return integrate.trapz(planck, (self.rsr[self.wavespace]))

    def make_tb2rad_lut(self, filepath):
        """Generate a Tb to radiance look-up table"""

        tb_ = np.arange(TB_MIN, TB_MAX, self.tb_resolution)
        rad = self.tb2radiance(tb_)
        
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
            ntb_therm = (tb_therm * self.tb_scale).astype('int16')
            ntb_nir = (tb_nir * self.tb_scale).astype('int16')
            lut = self.read_tb2rad_lut(lookuptable)
            start = int(lut['tb'][0] * self.tb_scale)
            end = int(lut['tb'][-1] * self.tb_scale)
            thermal_emiss_one = lut['radiance'][ntb_therm - start]
            ntb_nir = np.ma.masked_less(ntb_nir, start).filled(start)
            ntb_nir = np.ma.masked_greater(ntb_nir, end).filled(end)
            idx = ntb_nir - start
            l_nir = lut['radiance'][idx]
        else:
            thermal_emiss_one = self.tb2radiance(tb_therm)
            l_nir = self.tb2radiance(tb_nir)

        #print thermal_emiss_one.min(), thermal_emiss_one.max()
        #print l_nir.min(), l_nir.max()

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
        
        #nomin = np.where(np.less(nomin, 0), 0, nomin)
        #denom = np.where(np.less(denom, 0), 0, denom)

        #retv = np.where(np.greater(abs(denom), 
        #                           nomin.max()*EPSILON), 
        #                nomin/denom, nomin/(nomin.max()*EPSILON))
        #return np.ma.masked_where(retv < 0, retv)
        retv = nomin / denom
        retv = np.ma.masked_array(retv, mask = mask)
        return np.ma.masked_where(retv < 0, retv)
        
