#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017 Adam.Dybbroe

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
from six import integer_types

import h5py
import numpy as np
from scipy.interpolate import interpn

from pyspectral import get_config
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import (INSTRUMENTS, RAYLEIGH_LUT_DIRS,
                              download_luts, get_central_wave,
                              get_bandname_from_wavelength)

LOG = logging.getLogger(__name__)

ATMOSPHERES = {'subarctic summer': 4, 'subarctic winter': 5,
               'midlatitude summer': 6, 'midlatitude winter': 7,
               'tropical': 8, 'us-standard': 9}


class BandFrequencyOutOfRange(Exception):

    """Exception when the band frequency is out of the visible range"""
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

        if 'rural_aerosol' in kwargs and kwargs['rural_aerosol']:
            rayleigh_dir = RAYLEIGH_LUT_DIRS['rural_aerosol']
        else:
            rayleigh_dir = RAYLEIGH_LUT_DIRS['rayleigh_only']

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

        ext = atm_type.replace(' ', '_')
        lutname = "rayleigh_lut_{0}.h5".format(ext)
        self.reflectance_lut_filename = os.path.join(rayleigh_dir, lutname)

        if not os.path.exists(self.reflectance_lut_filename):
            LOG.warning(
                "No lut file %s on disk", self.reflectance_lut_filename)
            LOG.info("Will download from internet...")
            download_luts()

        if (not os.path.exists(self.reflectance_lut_filename) or
                not os.path.isfile(self.reflectance_lut_filename)):
            raise IOError('pyspectral file for Rayleigh scattering correction ' +
                          'does not exist! Filename = ' +
                          str(self.reflectance_lut_filename))

        LOG.debug('LUT filename: %s', str(self.reflectance_lut_filename))

    def get_effective_wavelength(self, bandname):
        """Get the effective wavelength with Rayleigh scattering in mind"""

        try:
            rsr = RelativeSpectralResponse(self.platform_name, self.sensor)
        except IOError:
            LOG.exception(
                "No spectral responses for this platform and sensor: %s %s", self.platform_name, self.sensor)
            if isinstance(bandname, (float, integer_types)):
                LOG.warning(
                    "Effective wavelength is set to the requested band wavelength = %f", bandname)
                return bandname
            raise

        if isinstance(bandname, str):
            bandname = self.sensor_bandnames.get(bandname, bandname)
        elif isinstance(bandname, (float, integer_types)):
            if not(0.4 < bandname < 0.8):
                raise BandFrequencyOutOfRange(
                    'Requested band frequency should be between 0.4 and 0.8 microns!')
            bandname = get_bandname_from_wavelength(bandname, rsr.rsr)

        wvl, resp = rsr.rsr[bandname][
            'det-1']['wavelength'], rsr.rsr[bandname]['det-1']['response']

        return get_central_wave(wvl, resp, weight=1. / wvl**4)

    def get_reflectance_lut(self):
        """Read the LUT with reflectances as a function of wavelength, satellite zenith
        secant, azimuth difference angle, and sun zenith secant

        """

        with h5py.File(self.reflectance_lut_filename, 'r') as h5f:
            tab = h5f['reflectance'][:]
            wvl = h5f['wavelengths'][:]
            azidiff = h5f['azimuth_difference'][:]
            satellite_zenith_secant = h5f['satellite_zenith_secant'][:]
            sun_zenith_secant = h5f['sun_zenith_secant'][:]

        return tab, wvl, azidiff, satellite_zenith_secant, sun_zenith_secant

    def get_reflectance(self, sun_zenith, sat_zenith, azidiff, bandname,
                        blueband=None):
        """Get the reflectance from the thre sun-sat angles."""
        # Get wavelength in nm for band:
        sun_zenith = np.clip(sun_zenith, 0, 88.)
        sunzsec = 1. / np.cos(np.deg2rad(sun_zenith))
        satzsec = 1. / np.cos(np.deg2rad(sat_zenith))

        shape = sun_zenith.shape

        wvl = self.get_effective_wavelength(bandname) * 1000.0
        rayl, wvl_coord, azid_coord, satz_sec_coord, sunz_sec_coord = self.get_reflectance_lut()

        if not(wvl_coord.min() < wvl < wvl_coord.max()):
            LOG.warning(
                "Effective wavelength for band %s outside 400-800 nm range!", str(bandname))
            LOG.info(
                "Set the rayleigh/aerosol reflectance contribution to zero!")
            return np.zeros(sun_zenith.shape)

        idx = np.sqrt((wvl_coord - wvl)**2).argsort()[0]
        wvl1 = wvl_coord[idx - 1]
        wvl2 = wvl_coord[idx]
        c_wvl = np.arange(wvl1, wvl2, 1.)
        #c_sunz = np.arange(1., 25., 0.1)
        sunzsec_max = min(sunzsec.max(), 25.)
        sunzsec_min = sunzsec.min()
        c_sunz = np.arange(sunzsec_min, sunzsec_max, 0.1)
        c_azi = np.arange(0., 180., 1.0)
        #c_satz = np.arange(1., 3., 0.1)
        satzsec_max = satzsec.max()
        satzsec_min = satzsec.min()
        c_satz = np.arange(satzsec_min, satzsec_max, 0.1)

        interp_mesh = np.array(np.meshgrid(c_wvl, c_sunz, c_azi, c_satz))
        interp_points = np.rollaxis(interp_mesh, 0, 5)
        interp_points = interp_points.reshape((interp_mesh.size // 4, 4))

        ipn = interpn(
            (wvl_coord, sunz_sec_coord,
             azid_coord, satz_sec_coord), rayl[:, :, :, :], interp_points)

        idx = (np.argsort(np.abs(c_satz - satzsec[:, :, np.newaxis]))[:, :, 0] +
               np.argsort(np.abs(c_azi - azidiff[:, :, np.newaxis]))[:, :, 0] * c_satz.shape[0] +
               np.argsort(np.abs(c_wvl - wvl))[0] * c_satz.shape[0] * c_azi.shape[0] +
               np.argsort(np.abs(c_sunz - sunzsec[:, :, np.newaxis]))[:, :, 0] *
               c_satz.shape[0] * c_azi.shape[0] * c_wvl.shape[0])

        res = ipn[idx].reshape(shape) * 100
        if blueband is not None:
            res = np.where(np.less(blueband, 20.), res,
                           (1 - (blueband - 20) / 80) * res)

        return np.clip(res, 0, 100)


if __name__ == "__main__":

    this = Rayleigh('Suomi-NPP', 'viirs')
    # SUNZ = np.arange(200000).reshape(400, 500) * 0.0004
    # SATZ = np.arange(200000).reshape(400, 500) * 0.00025
    # AZIDIFF = np.arange(200000).reshape(400, 500) * 0.0009
    # rfl = this.get_reflectance(SUNZ, SATZ, AZIDIFF, 'M4')

    SHAPE = (1000, 3000)
    NDIM = SHAPE[0] * SHAPE[1]
    SUNZ = np.arange(
        NDIM / 2, NDIM + NDIM / 2).reshape(SHAPE) * 60. / float(NDIM)
    SATZ = np.arange(NDIM).reshape(SHAPE) * 60. / float(NDIM)
    AZIDIFF = np.arange(NDIM).reshape(SHAPE) * 179.9 / float(NDIM)
    rfl = this.get_reflectance(SUNZ, SATZ, AZIDIFF, 'M4')
