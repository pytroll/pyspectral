#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014-2018 Adam.Dybbroe

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

"""Conversion between radiances and brightness temperatures for the IR bands of
various satellite sensors
"""

import numpy as np
from pyspectral.blackbody import blackbody, blackbody_wn
from pyspectral.utils import BANDNAMES
from pyspectral.utils import get_bandname_from_wavelength
from pyspectral.blackbody import (H_PLANCK, K_BOLTZMANN, C_SPEED)
from pyspectral.utils import convert2wavenumber
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import WAVE_NUMBER
from pyspectral.utils import WAVE_LENGTH

from numbers import Number
from scipy import integrate

import logging
LOG = logging.getLogger(__name__)

BLACKBODY_FUNC = {WAVE_LENGTH: blackbody,
                  WAVE_NUMBER: blackbody_wn}

EPSILON = 0.01
TB_MIN = 150.
TB_MAX = 360.

# Meteosat SEVIRI regression parameters according to documentation
# (PDF_EFFECT_RAD_TO_BRIGHTNESS.pdf).
#
# Tb = C2 * νc/{α * log[C1*νc**3 / L + 1]} - β/α
#
# L = C1 * νc**3 / (exp (C2 νc / [αTb + β]) − 1)
#
# C1 = 2 * h * c**2 and C2 = hc/k
#
# Units are cm-1 for the channel/band central wavenumber, K for the beta
# parameter, and the alpha parameter is dimensionless:
#
SEVIRI = {'IR3.9': {'Meteosat-8': [2567.330, 0.9956, 3.410],
                    'Meteosat-9': [2568.832, 0.9954, 3.438],
                    'Meteosat-10': [],
                    },
          'WV6.2': {'Meteosat-8': [1598.103, 0.9962, 2.218],
                    'Meteosat-9': [1600.548, 0.9963, 2.185],
                    },
          'WV7.3': {'Meteosat-8': [1362.081, 0.9991, 0.478],
                    'Meteosat-9': [1360.330, 0.9991, 0.470],
                    },
          'IR8.7': {'Meteosat-8': [1149.069, 0.9996, 0.179],
                    'Meteosat-9': [1148.620, 0.9996, 0.179],
                    },
          'IR9.7': {'Meteosat-8': [1034.343, 0.9999, 0.060],
                    'Meteosat-9': [1035.289, 0.9999, 0.056],
                    },
          'IR10.8': {'Meteosat-8': [930.647, 0.9983, 0.625],
                     'Meteosat-9': [931.700, 0.9983, 0.640],
                     },
          'IR12.0': {'Meteosat-8': [839.660, 0.9988, 0.397],
                     'Meteosat-9': [836.445, 0.9988, 0.408],
                     },
          'IR13.4': {'Meteosat-8': [752.387, 0.9981, 0.578],
                     'Meteosat-9': [751.792, 0.9981, 0.561],
                     },
          }


class RadTbConverter(object):

    """A radiance to brightness temperature calculator.

    It does the conversion based on direct use of the band relative
    spectral response functions.
    """

    def __init__(self, platform_name, instrument, band, **options):
        """E.g.:
        platform_name = 'Meteosat-9'
        instrument = 'seviri'
        band = 3.75
        """
        self.platform_name = platform_name
        self.instrument = instrument
        self.response = None
        self.wavelength_or_wavenumber = None
        self.bandname = None
        self.bandwavelength = None
        self.band = band

        self.wavespace = options.get('wavespace', WAVE_LENGTH)
        if self.wavespace not in [WAVE_LENGTH, WAVE_NUMBER]:
            raise AttributeError('Wave space not {0} or {1}!'.format(WAVE_LENGTH,
                                                                     WAVE_NUMBER))

        self._wave_unit = 'm'
        self._wave_si_scale = 1.0

        self.detector = options.get('detector', 'det-1')
        self.tb_resolution = options.get('tb_resolution', 0.1)
        self.tb_scale = 1. / self.tb_resolution

        self.blackbody_function = BLACKBODY_FUNC[self.wavespace]
        self.rsr_integral = 1.0

        self._get_rsr()

    def _get_rsr(self):
        """
        Get the relative spectral responses from file, find the bandname, and
        convert to the requested wave-spave (wavelength or wave number)

        """
        sensor = RelativeSpectralResponse(self.platform_name, self.instrument)

        if self.wavespace == WAVE_NUMBER:
            LOG.debug("Converting to wavenumber...")
            self.rsr, info = convert2wavenumber(sensor.rsr)
        else:
            self.rsr = sensor.rsr
            info = {'unit': sensor.unit, 'si_scale': sensor.si_scale}

        self._wave_unit = info['unit']
        self._wave_si_scale = info['si_scale']

        if isinstance(self.band, str):
            self.bandname = BANDNAMES.get(self.instrument, BANDNAMES['generic']).get(self.band, self.band)
        elif isinstance(self.band, Number):
            self.bandwavelength = self.band
            self.bandname = get_bandname_from_wavelength(self.instrument, self.band, self.rsr)

        self.wavelength_or_wavenumber = (self.rsr[self.bandname][self.detector][self.wavespace] *
                                         self._wave_si_scale)
        self.response = self.rsr[self.bandname][self.detector]['response']
        # Get the integral of the spectral response curve:
        self.rsr_integral = np.trapz(self.response, self.wavelength_or_wavenumber)

    def _getsatname(self):
        """
        Get the satellite name used in the rsr-reader, from the platform
        and number

        """
        if self.platform_name.startswith("Meteosat"):
            return self.platform_name
        else:
            raise NotImplementedError(
                'Platform {0} not yet supported...'.format(self.platform_name))

    def tb2radiance(self, tb_, **kwargs):
        """Get the radiance from the brightness temperature (Tb) given the
        band name.

        Input:
          tb_: Brightness temperature of the band (self.band)

        Optional arguments:
          lut: If not none, this is a Look Up Table with tb and radiance values
            which will be used for the conversion. Default is None.

          normalized: If True, the derived radiance values are the spectral radiances for the band.
            If False the radiance is the band integrated radiance. Default is True.

        """
        lut = kwargs.get('lut', None)
        normalized = kwargs.get('normalized', True)

        if self.wavespace == WAVE_NUMBER:
            if normalized:
                unit = 'W/m^2 sr^-1 (m^-1)^-1'
            else:
                unit = 'W/m^2 sr^-1'
            scale = 1.0
        else:
            if normalized:
                unit = 'W/m^2 sr^-1 m^-1'
            else:
                unit = 'W/m^2 sr^-1'
            scale = 1.0

        if lut:
            ntb = (tb_ * self.tb_scale).astype('int16')
            start = int(lut['tb'][0] * self.tb_scale)
            retv = {}
            bounds = 0, lut['radiance'].shape[0] - 1
            index = np.clip(ntb - start, bounds[0], bounds[1])
            retv['radiance'] = lut['radiance'][index]
            if retv['radiance'].ravel().shape[0] == 1:
                retv['radiance'] = retv['radiance'][0]
            retv['unit'] = unit
            retv['scale'] = scale
            return retv

        planck = self.blackbody_function(self.wavelength_or_wavenumber, tb_) * self.response
        if normalized:
            radiance = integrate.trapz(planck, self.wavelength_or_wavenumber) / self.rsr_integral
        else:
            radiance = integrate.trapz(planck, self.wavelength_or_wavenumber)

        return {'radiance': radiance,
                'unit': unit,
                'scale': scale}

    def make_tb2rad_lut(self, filepath, normalized=True):
        """Generate a Tb to radiance look-up table"""
        tb_ = np.arange(TB_MIN, TB_MAX, self.tb_resolution)
        retv = self.tb2radiance(tb_, normalized=normalized)
        rad = retv['radiance']
        np.savez(filepath, tb=tb_, radiance=rad.compressed())

    @staticmethod
    def read_tb2rad_lut(filepath):
        """Read the Tb to radiance look-up table"""
        retv = np.load(filepath, 'r')
        return retv

    def radiance2tb(self, rad):
        """
        Get the Tb from the radiance using the Planck function and the central wavelength of the band

        rad:
            Radiance in SI units
        """
        return radiance2tb(rad, self.rsr[self.bandname][self.detector]['central_wavelength'] * 1e-6)


def radiance2tb(rad, wavelength):
    """
    Get the Tb from the radiance using the Planck function

    rad:
        Radiance in SI units
    wavelength:
        Wavelength in SI units (meter)
    """
    from pyspectral.blackbody import blackbody_rad2temp as rad2temp
    return rad2temp(wavelength, rad)


class SeviriRadTbConverter(RadTbConverter):

    """A radiance to brightness temperature calculator for SEVIRI based on
     tabulated standard values using non-linear regression methods, and thus no
     use of off line relative spectral response functions

    """

    def __init__(self, platform_name, band, **kwargs):
        """
        E.g.:
        platform_name = Meteosat-9
        band = 3.75

        """
        super(SeviriRadTbConverter, self).__init__(platform_name, 'seviri',
                                                   band, **kwargs)

        if isinstance(self.band, str):
            self.bandname = BANDNAMES.get(self.instrument, BANDNAMES['generic']).get(self.band, self.band)
        else:
            raise AttributeError('Band name provided as a string is required')

    def _get_rsr(self):
        """Overload the _get_rsr method, since RSR data are ignored here"""
        pass

    def radiance2tb(self, rad):
        """Get the Tb from the radiance using the simple non-linear regression
        method.

        rad: Radiance in units = 'mW/m^2 sr^-1 (cm^-1)^-1'

        """
        #
        # Tb = C2 * νc/{α * log[C1*νc**3 / L + 1]} - β/α
        #
        # C1 = 2 * h * c**2 and C2 = hc/k
        #
        c_1 = 2 * H_PLANCK * C_SPEED ** 2
        c_2 = H_PLANCK * C_SPEED / K_BOLTZMANN

        vc_ = SEVIRI[self.bandname][self.platform_name][0]
        # Multiply by 100 to get SI units!
        vc_ *= 100.0
        alpha = SEVIRI[self.bandname][self.platform_name][1]
        beta = SEVIRI[self.bandname][self.platform_name][2]

        tb_ = c_2 * vc_ / \
            (alpha * np.log(c_1 * vc_ ** 3 / rad + 1)) - beta / alpha

        return tb_

    def tb2radiance(self, tb_, **kwargs):
        """Get the radiance from the Tb using the simple non-linear regression
        method. SI units of course!
        """
        # L = C1 * νc**3 / (exp (C2 νc / [αTb + β]) − 1)
        #
        # C1 = 2 * h * c**2 and C2 = hc/k
        #
        lut = kwargs.get('lut', None)
        normalized = kwargs.get('normalized', True)

        if lut is not None:
            raise NotImplementedError('Using a tb-radiance LUT is not yet supported')
        if not normalized:
            raise NotImplementedError('Deriving the band integrated radiance is not supported')

        c_1 = 2 * H_PLANCK * C_SPEED ** 2
        c_2 = H_PLANCK * C_SPEED / K_BOLTZMANN

        vc_ = SEVIRI[self.bandname][self.platform_name][0]
        # Multiply by 100 to get SI units!
        vc_ *= 100.0
        alpha = SEVIRI[self.bandname][self.platform_name][1]
        beta = SEVIRI[self.bandname][self.platform_name][2]

        radiance = c_1 * vc_ ** 3 / \
            (np.exp(c_2 * vc_ / (alpha * tb_ + beta)) - 1)

        unit = 'W/m^2 sr^-1 (m^-1)^-1'
        scale = 1.0
        return {'radiance': radiance,
                'unit': unit,
                'scale': scale}
