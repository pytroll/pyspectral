#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

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

"""
"""

import ConfigParser
import os

import logging
LOG = logging.getLogger(__name__)

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")


import numpy as np
import h5py

from pyspectral.utils import get_central_wave
from pyspectral.rsr_reader import RelativeSpectralResponse

ATMOSPHERES = {'subarctic summer': 4, 'subarctic winter': 5,
               'midlatitude summer': 6, 'midlatitude winter': 7,
               'tropical': 8, 'us-standard': 9}

from pyspectral.utils import (INSTRUMENTS,
                              get_rayleigh_reflectance)


class Rayleigh(object):

    """Container for the Rayleigh scattering correction of satellite imager short
    wave bands

    """

    def __init__(self, platform_name, sensor, **kwargs):
        self.platform_name = platform_name
        self.sensor = sensor
        self.coeff_filename = None

        if 'atmosphere' in kwargs:
            atm_type = kwargs['atmosphere']
        else:
            atm_type = 'subarctic summer'

        if atm_type not in ATMOSPHERES.keys():
            LOG.error("Atmosphere type %s not supported", atm_type)

        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception('Failed reading configuration file: %s',
                          str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items('general', raw=True):
            options[option] = value

        # Try fix instrument naming
        instr = INSTRUMENTS.get(platform_name, sensor)
        if instr != sensor:
            sensor = instr
            LOG.warning("Inconsistent sensor/satellite input - " +
                        "sensor set to %s", sensor)

        self.sensor = sensor.replace('/', '')

        rayleigh_dir = options['rayleigh_dir']
        self.coeff_filename = os.path.join(rayleigh_dir,
                                           'poly_fit_parameters_const_azidiff_extended.h5')

        LOG.debug('Filename: %s', str(self.coeff_filename))

        if (not os.path.exists(self.coeff_filename) or
                not os.path.isfile(self.coeff_filename)):
            raise IOError('pyspectral file for Rayleigh scattering correction ' +
                          'does not exist! Filename = ' +
                          str(self.coeff_filename))

    def get_effective_wavelength(self, bandname):
        """Get the effective wavelength with Rayleigh scattering in mind"""

        rsr = RelativeSpectralResponse(self.platform_name, self.sensor)
        wvl, resp = rsr.rsr[bandname][
            'det-1']['wavelength'], rsr.rsr[bandname]['det-1']['response']

        return get_central_wave(wvl, resp, weight=1. / wvl**4)

    def get_poly_coeff(self):
        """Extract the polynomial fit coefficients from file"""

        with h5py.File(self.coeff_filename, 'r') as h5f:
            tab = h5f['coeff'][:]
            wvl = h5f['wavelengths'][:]
            azidiff = h5f['azimuth_difference'][:]

        return tab, wvl, azidiff

    def get_reflectance(self, sun_zenith, sat_zenith, azidiff, bandname):
        """Get the refelctance from the three sun-sat angles"""

        # Get wavelength in nm for band:
        wvl = self.get_effective_wavelength(bandname) * 1000.0
        coeff, wvl_coord, azid_coord = self.get_poly_coeff()

        idx = np.sqrt((wvl_coord - wvl)**2).argsort()[0]
        wvl1 = wvl_coord[idx]
        wvl2 = wvl_coord[idx + 1]

        shape = sun_zenith.shape
        c1_ = coeff[idx, np.round(azidiff).astype('i').ravel(), :].transpose().reshape(
            21, shape[0], shape[1])
        c2_ = coeff[idx + 1, np.round(azidiff).astype('i').ravel(), :].transpose().reshape(
            21, shape[0], shape[1])
        res1 = get_rayleigh_reflectance(c1_, sun_zenith, sat_zenith)
        res2 = get_rayleigh_reflectance(c2_, sun_zenith, sat_zenith)

        # Bilinear interpolation
        res = ((res2 - res1) * wvl + res1 * wvl2 - res2 * wvl1) / (wvl2 - wvl1)

        return res
