#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>
#   Martin Raspaud <martin.raspaud@smhi.se>

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

import logging
import os
from os.path import expanduser

import h5py
import numpy as np

from pyspectral import BUILTIN_CONFIG_FILE, CONFIG_FILE, get_config
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import (BANDNAMES, INSTRUMENTS, get_central_wave,
                              get_rayleigh_reflectance)

LOG = logging.getLogger(__name__)


ATMOSPHERES = {'subarctic summer': 4, 'subarctic winter': 5,
               'midlatitude summer': 6, 'midlatitude winter': 7,
               'tropical': 8, 'us-standard': 9}

HTTP_RAYLEIGH_ONLY_LUTS = "https://dl.dropboxusercontent.com/u/37482654/rayleigh_only/rayleigh_luts_rayleigh_only.tgz"
HTTP_RURAL_AEROSOLS_LUTS = "https://dl.dropboxusercontent.com/u/37482654/rural_aerosol/rayleigh_luts_rural_aerosol.tgz"


HOME = expanduser("~")
LOCAL_DEST = os.path.join(HOME, ".local/share/pyspectral")
try:
    os.makedirs(LOCAL_DEST)
except OSError:
    if not os.path.isdir(LOCAL_DEST):
        raise


class BandFrequencyOutOfRange(Exception):
    pass


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

        conf = get_config()

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

        try:
            rsr = RelativeSpectralResponse(self.platform_name, self.sensor)
        except IOError:
            LOG.exception(
                "No spectral responses for this platform and sensor: %s %s", self.platform_name, self.sensor)
            if isinstance(bandname, (float, int, long)):
                LOG.warning(
                    "Effective wavelength is set to the requested band wavelength = %f", bandname)
                return bandname
            raise

        if isinstance(bandname, str):
            bandname = self.sensor_bandnames.get(bandname, bandname)
        elif isinstance(bandname, (float, int, long)):
            if bandname < 0.4 or bandname > 0.8:
                raise BandFrequencyOutOfRange(
                    'Requested band frequency should be between 0.4 and 0.8 microns!')
            bandname = get_bandname_from_wavelength(bandname, rsr)

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
        """Get the reflectance from the thre sun-sat angles."""
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
        sun_zenith = np.clip(sun_zenith, 0, 88.)
        res1 = get_rayleigh_reflectance(c1_, sun_zenith, sat_zenith)
        res2 = get_rayleigh_reflectance(c2_, sun_zenith, sat_zenith)

        # Bilinear interpolation
        res = ((res2 - res1) * wvl + res1 * wvl2 - res2 * wvl1) / (wvl2 - wvl1)
        res *= 100

        if blueband is not None:
            res = np.where(np.less(blueband, 20.), res,
                           (1 - (blueband - 20) / 80) * res)

        return np.clip(res, 0, 100)


def get_bandname_from_wavelength(wavelength, rsr):
    """Get the bandname from h5 rsr provided the approximate wavelength."""
    epsilon = 0.1
    # channel_list = [channel for channel in rsr.rsr if abs(
    # rsr.rsr[channel]['det-1']['central_wavelength'] - wavelength) < epsilon]

    chdist_min = 2.0
    chfound = None
    for channel in rsr.rsr:
        chdist = abs(
            rsr.rsr[channel]['det-1']['central_wavelength'] - wavelength)
        if chdist < chdist_min and chdist < epsilon:
            chdist_min = chdist
            chfound = channel

    return BANDNAMES.get(chfound, chfound)


def download_luts():
    """Download the luts from internet."""
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
