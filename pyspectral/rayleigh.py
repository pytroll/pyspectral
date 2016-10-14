#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

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

"""Rayleigh correction of shortwave imager bands in the wavelength range 400 to
800 nm

"""

import ConfigParser
import os

import logging
LOG = logging.getLogger(__name__)

BASE_PATH = os.path.sep.join(os.path.dirname(
    os.path.realpath(__file__)).split(os.path.sep)[:-1])
# FIXME: Use package_resources?
PACKAGE_CONFIG_PATH = os.path.join(BASE_PATH, 'etc')
BUILTIN_CONFIG_FILE = os.path.join(PACKAGE_CONFIG_PATH, 'pyspectral.cfg')

CONFIG_FILE = os.environ.get('PSP_CONFIG_FILE')

if CONFIG_FILE is not None and (not os.path.exists(CONFIG_FILE) or
                                not os.path.isfile(CONFIG_FILE)):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")

import numpy as np
import h5py

from pyspectral.utils import get_central_wave
from pyspectral.rsr_reader import RelativeSpectralResponse

ATMOSPHERES = {'subarctic summer': 4, 'subarctic winter': 5,
               'midlatitude summer': 6, 'midlatitude winter': 7,
               'tropical': 8, 'us-standard': 9}

HTTP_RAYLEIGH_ONLY_LUTS = "https://dl.dropboxusercontent.com/u/37482654/rayleigh_only/rayleigh_luts_rayleigh_only.tgz"
HTTP_RURAL_AEOROSOLS_LUTS = "https://dl.dropboxusercontent.com/u/37482654/rural_aerosol/rayleigh_luts_rural_aerosol.tgz"

from pyspectral.utils import (INSTRUMENTS,
                              get_rayleigh_reflectance)

from os.path import expanduser
HOME = expanduser("~")
LOCAL_DEST = os.path.join(HOME, ".local/share/pyspectral")
try:
    os.makedirs(LOCAL_DEST)
except OSError:
    if not os.path.isdir(LOCAL_DEST):
        raise


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

        LOG.info("Atmosphere chosen: %s", atm_type)

        conf = ConfigParser.ConfigParser()
        conf.read(BUILTIN_CONFIG_FILE)
        if CONFIG_FILE is not None:
            try:
                conf.read(CONFIG_FILE)
            except ConfigParser.NoSectionError:
                LOG.info('Failed reading configuration file: %s',
                         str(CONFIG_FILE))

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

        # Conversion from standard band names to pyspectral band naming.
        # Preferably take from config! FIXME!
        self.sensor_bandnames = {'B01': 'ch1',
                                 'B02': 'ch2',
                                 'B03': 'ch3',
                                 'M03': 'M3',
                                 'M04': 'M4',
                                 'M05': 'M5',
                                 }

        rayleigh_dir = LOCAL_DEST
        #rayleigh_dir = options['rayleigh_dir']
        ext = atm_type.replace(' ', '_')
        lutname = "rayleigh_lut_const_azidiff_%s.h5" % ext
        self.coeff_filename = os.path.join(rayleigh_dir, lutname)

        if not os.path.exists(self.coeff_filename):
            LOG.warning("No lut file %s on disk", self.coeff_filename)
            LOG.info("Will download from internet...")
            download_luts()

        if (not os.path.exists(self.coeff_filename) or
                not os.path.isfile(self.coeff_filename)):
            raise IOError('pyspectral file for Rayleigh scattering correction ' +
                          'does not exist! Filename = ' +
                          str(self.coeff_filename))

        LOG.debug('LUT filename: %s', str(self.coeff_filename))

    def get_effective_wavelength(self, bandname):
        """Get the effective wavelength with Rayleigh scattering in mind"""

        bandname = self.sensor_bandnames.get(bandname, bandname)
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

    def get_reflectance(self, sun_zenith, sat_zenith, azidiff, bandname,
                        blueband=None):
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

        if blueband == None:
            return res * 100

        return np.where(np.less(blueband, 20.), res,
                        (1 - (blueband - 20) / 80) * res) * 100


def download_luts():
    """Download the luts from internet"""

    #
    import tarfile
    import requests
    from tqdm import tqdm

    response = requests.get(HTTP_RAYLEIGH_ONLY_LUTS)
    response = requests.get(HTTP_RURAL_AEROSOLS_LUTS)
    filename = os.path.join(LOCAL_DEST, "rayleigh_luts_rayleigh_only.tgz")
    with open(filename, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)

    tar = tarfile.open(filename)
    tar.extractall(LOCAL_DEST)
    tar.close()
    os.remove(filename)
