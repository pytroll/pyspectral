#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015, 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>
#   Panu Lahtinen <panu.lahtinen@fmi.fi>

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

import os
import numpy as np
from pyspectral.solar import (SolarIrradianceSpectrum,
                              TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
from pyspectral.utils import BANDNAMES
from pyspectral.radiance_tb_conversion import RadTbConverter
from pyspectral import get_config

import logging
LOG = logging.getLogger(__name__)


WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'

EPSILON = 0.01
TB_MIN = 150.
TB_MAX = 360.


class Calculator(RadTbConverter):

    """A thermal near-infrared (e.g. 3.7 micron) band reflectance calculator.

    Given the relative spectral response of the NIR band, the solar zenith
    angle, and the brightness temperatures of the NIR and the Thermal bands,
    derive the solar reflectance for the NIR band removing the thermal
    (terrestrial) part.  The in-band solar flux over the NIR band is
    optional. If not provided, it will be calculated here!

    The relfectance calculated is without units and should be between 0 and 1.
    """

    def __init__(self, platform_name, instrument, band,
                 solar_flux=None, **kwargs):
        """Init"""
        super(Calculator, self).__init__(platform_name, instrument,
                                         band, method=1, **kwargs)

        self.bandname = None
        self.bandwavelength = None

        if isinstance(band, str):
            self.bandname = BANDNAMES.get(band, band)
        elif isinstance(band, (int, long, float)):
            self.bandwavelength = band

        if self.bandname is None:
            epsilon = 0.1
            channel_list = [channel for channel in self.rsr if abs(
                self.rsr[channel]['det-1']['central_wavelength'] - self.bandwavelength) < epsilon]
            self.bandname = BANDNAMES.get(channel_list[0], channel_list[0])

        options = {}
        conf = get_config()
        for option, value in conf.items(platform_name + '-' + instrument,
                                        raw=True):
            options[option] = value

        if solar_flux is None:
            self._get_solarflux()
        else:
            self.solar_flux = solar_flux
        self._rad3x = None
        self._rad3x_t11 = None
        self._solar_radiance = None
        self._rad3x_correction = 1.0
        self._r3x = None
        self._e3x = None

        if 'detector' in kwargs:
            self.detector = kwargs['detector']
        else:
            self.detector = 'det-1'

        resp = self.rsr[self.bandname][self.detector]['response']
        wv_ = self.rsr[self.bandname][self.detector][self.wavespace]
        self.rsr_integral = np.trapz(resp, wv_)

        if 'tb2rad_lut_filename' in options:
            self.lutfile = options['tb2rad_lut_filename']
            if not self.lutfile.endswith('.npz'):
                self.lutfile = self.lutfile + '.npz'

            if not os.path.exists(os.path.dirname(self.lutfile)):
                LOG.warning(
                    "Directory %s does not exist! Check config file" % os.path.dirname(self.lutfile))
                self.lutfile = os.path.join(
                    '/tmp', os.path.basename(self.lutfile))

            LOG.info("lut filename: " + str(self.lutfile))
            if not os.path.exists(self.lutfile):
                self.make_tb2rad_lut(self.bandname,
                                     self.lutfile)
                self.lut = self.read_tb2rad_lut(self.lutfile)
                LOG.info("LUT file created")
            else:
                self.lut = self.read_tb2rad_lut(self.lutfile)
                LOG.info("File was there and has been read!")
        else:
            LOG.info("No lut filename available in config file. "
                     "No lut will be used")
            self.lutfile = None
            self.lut = None

    def derive_rad39_corr(self, bt11, bt13, method='rosenfeld'):
        """Derive the 3.9 radiance correction factor to account for the
        attenuation of the emitted 3.9 radiance by CO2
        absorption. Requires the 11 micron window band and the 13.4
        CO2 absorption band, as e.g. available on SEVIRI. Currently
        only supports the Rosenfeld method
        """
        if method != 'rosenfeld':
            raise AttributeError("Only CO2 correction for SEVIRI using "
                                 "the Rosenfeld equation is supported!")

        LOG.debug("Derive the 3.9 micron radiance CO2 correction coefficent")
        self._rad3x_correction = (bt11 - 0.25 * (bt11 - bt13)) ** 4 / bt11 ** 4

    def _get_solarflux(self):
        """Derive the in-band solar flux from rsr over the Near IR band (3.7
        or 3.9 microns)
        """
        solar_spectrum = \
            SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM,
                                    dlambda=0.0005,
                                    wavespace=self.wavespace)
        self.solar_flux = \
            solar_spectrum.inband_solarflux(self.rsr[self.bandname])

    def emissive_part_3x(self, tb=True):
        """Get the emissive part of the 3.x band"""
        try:
            # Emissive part:
            # self._e3x = self._rad3x_t11 * (1 -
            self._e3x = self._rad3x * (1 -
                                       np.ma.masked_outside(self._r3x, 0, 1,
                                                            copy=False))
        except TypeError:
            LOG.warning(
                "Couldn't derive the emissive part \n" +
                "Please derive the relfectance prior to requesting the emissive part")

        if tb:
            # FIXME! Get the correct central wavelength
            return self.radiance2tb(self._e3x, 3.9e-6)
        else:
            return self._e3x

    def reflectance_from_tbs(self, sun_zenith, tb_near_ir, tb_thermal,
                             tb_ir_co2=None):
        """The relfectance calculated is without units and should be between 0
        and 1.

        Inputs:

          sun_zenith: Sun zenith angle for every pixel - in degrees

          tb_near_ir: The 3.7 (or 3.9 or equivalent) IR Tb's at every pixel
                      (Kelvin)

          tb_thermal: The 10.8 (or 11 or 12 or equivalent) IR Tb's at every
                      pixel (Kelvin)

          tb_ir_co2: The 13.4 micron channel (or similar - co2 absorption band)
                     brightness temperatures at every pixel. If None, no CO2
                     absorption correction will be applied.

        """
        if np.isscalar(tb_near_ir):
            tb_nir = np.array([tb_near_ir, ])
        else:
            tb_nir = np.array(tb_near_ir)

        if np.isscalar(tb_thermal):
            tb_therm = np.array([tb_thermal, ])
        else:
            tb_therm = np.array(tb_thermal)

        if tb_therm.shape != tb_nir.shape:
            raise ValueError('Dimensions do not match! %s and %s' %
                             (str(tb_therm.shape), str(tb_nir.shape)))

        if tb_ir_co2 is None:
            co2corr = False
            tbco2 = None
        else:
            co2corr = True
            if np.isscalar(tb_ir_co2):
                tbco2 = np.array([tb_ir_co2, ])
            else:
                tbco2 = np.array(tb_ir_co2)

        if self.instrument == 'seviri':
            ch3xname = 'IR3.9'
        elif self.instrument == 'modis':
            ch3xname = '20'
        elif self.instrument in ["avhrr", "avhrr3", "avhrr/3"]:
            ch3xname = 'ch3b'
        elif self.instrument == 'ahi':
            ch3xname = 'ch7'
        elif self.instrument == 'viirs':
            ch3xname = 'M12'
        else:
            raise NotImplementedError('Not yet support for this '
                                      'instrument %s' % str(self.instrument))

        if not self.rsr:
            raise NotImplementedError("Reflectance calculations without "
                                      "rsr not yet supported!")
            # retv = self.tb2radiance_simple(tb_therm, ch3xname)
            # print("tb2radiance_simple conversion: " + str(retv))
            # thermal_emiss_one = retv['radiance']
            # retv = self.tb2radiance_simple(tb_nir, ch3xname)
            # print("tb2radiance_simple conversion: " + str(retv))
            # l_nir = retv['radiance']
        else:
            # Assume rsr in in microns!!!
            # FIXME!
            scale = self.rsr_integral * 1e-6
            retv = self.tb2radiance(tb_therm, ch3xname, self.lut)
            # print("tb2radiance conversion: " + str(retv))
            thermal_emiss_one = retv['radiance'] * scale
            retv = self.tb2radiance(tb_nir, ch3xname, self.lut)
            # print("tb2radiance conversion: " + str(retv))
            l_nir = retv['radiance'] * scale

        if thermal_emiss_one.ravel().shape[0] < 10:
            LOG.info('thermal_emiss_one = %s', str(thermal_emiss_one))
        if l_nir.ravel().shape[0] < 10:
            LOG.info('l_nir = %s', str(l_nir))

        sunz = np.ma.masked_outside(sun_zenith, 0.0, 88.0)
        sunzmask = sunz.mask
        sunz = sunz.filled(88.)

        mu0 = np.cos(np.deg2rad(sunz))
        # mu0 = np.where(np.less(mu0, 0.1), 0.1, mu0)
        self._rad3x = l_nir
        self._rad3x_t11 = thermal_emiss_one
        self._solar_radiance = 1. / np.pi * self.solar_flux * mu0

        # CO2 correction to the 3.9 radiance, only if tbs of a co2 band around
        # 13.4 micron is provided:
        if co2corr:
            self.derive_rad39_corr(tb_therm, tbco2)
        else:
            self._rad3x_correction = 1.0

        # mask = thermal_emiss_one > l_nir

        nomin = l_nir - self._rad3x_t11 * self._rad3x_correction
        LOG.debug("Shapes: %s  %s", str(mu0.shape),
                  str(self._rad3x_t11.shape))
        denom = self._solar_radiance - \
            self._rad3x_t11 * self._rad3x_correction

        r3x = nomin / denom
        # r3x = np.ma.masked_array(r3x, mask=mask)
        # r3x = np.ma.masked_where(r3x < 0, r3x)
        # Do some further masking, also with sun-zenith:
        # r3x = np.ma.masked_outside(r3x, 0.0, 10.0)  # * 100.  # Percent!
        # if np.ma.is_masked(tb_nir):
        #    r3x = np.ma.masked_where(tb_nir.mask, r3x).filled(0)
        self._r3x = np.ma.masked_where(sunzmask, r3x)

        # Reflectances should be between 0 and 1, but values above 1 is
        # perfectly possible and okay! (Multiply by 100 to get reflectances
        # in percent)
        return self._r3x
