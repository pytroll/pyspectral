#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017 Pytroll

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
                              AEROSOL_TYPES, ATMOSPHERES,
                              download_luts, get_central_wave,
                              get_bandname_from_wavelength)

LOG = logging.getLogger(__name__)

WITH_CYTHON = True
try:
    from geotiepoints.multilinear import MultilinearInterpolator
except ImportError:
    LOG.warning(
        "Couldn't import fast multilinear interpolation with Cython.")
    LOG.warning("Check your geotiepoints installation!")
    WITH_CYTHON = False


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

        if 'aerosol_type' in kwargs:
            if kwargs['aerosol_type'] not in AEROSOL_TYPES:
                raise AttributeError('Aerosol type not supported! ' +
                                     'Need to be one of {0}'.format(str(AEROSOL_TYPES)))
            aerosol_type = kwargs['aerosol_type']
        else:
            aerosol_type = 'rayleigh_only'

        rayleigh_dir = RAYLEIGH_LUT_DIRS[aerosol_type]

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
            download_luts(aerosol_type=aerosol_type)

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
        """Get the reflectance from the three sun-sat angles."""
        # Get wavelength in nm for band:
        wvl = self.get_effective_wavelength(bandname) * 1000.0
        rayl, wvl_coord, azid_coord, satz_sec_coord, sunz_sec_coord = self.get_reflectance_lut()

        clip_angle = np.rad2deg(np.arccos(1. / sunz_sec_coord.max()))
        sun_zenith = np.clip(np.asarray(sun_zenith), 0, clip_angle)
        sunzsec = 1. / np.cos(np.deg2rad(sun_zenith))
        clip_angle = np.rad2deg(np.arccos(1. / satz_sec_coord.max()))
        sat_zenith = np.clip(np.asarray(sat_zenith), 0, clip_angle)
        satzsec = 1. / np.cos(np.deg2rad(np.asarray(sat_zenith)))

        shape = sun_zenith.shape

        if not(wvl_coord.min() < wvl < wvl_coord.max()):
            LOG.warning(
                "Effective wavelength for band %s outside 400-800 nm range!", str(bandname))
            LOG.info(
                "Set the rayleigh/aerosol reflectance contribution to zero!")
            return np.zeros(shape)

        idx = np.searchsorted(wvl_coord, wvl)
        wvl1 = wvl_coord[idx - 1]
        wvl2 = wvl_coord[idx]

        fac = (wvl2 - wvl) / (wvl2 - wvl1)

        raylwvl = fac * rayl[idx - 1, :, :, :] + (1 - fac) * rayl[idx, :, :, :]

        import time
        tic = time.time()

        if WITH_CYTHON:
            smin = [sunz_sec_coord[0], azid_coord[0], satz_sec_coord[0]]
            smax = [sunz_sec_coord[-1], azid_coord[-1], satz_sec_coord[-1]]
            orders = [
                len(sunz_sec_coord), len(azid_coord), len(satz_sec_coord)]
            f_3d_grid = raylwvl

            minterp = MultilinearInterpolator(smin, smax, orders)
            minterp.set_values(np.atleast_2d(f_3d_grid.ravel()))

            interp_points2 = np.vstack((np.asarray(sunzsec).ravel(),
                                        np.asarray(180 - azidiff).ravel(),
                                        np.asarray(satzsec).ravel()))

            ipn = minterp(interp_points2).reshape(shape)
        else:
            interp_points = np.dstack((np.asarray(sunzsec),
                                       np.asarray(180. - azidiff),
                                       np.asarray(satzsec)))

            ipn = interpn((sunz_sec_coord, azid_coord, satz_sec_coord),
                          raylwvl[:, :, :], interp_points)

        LOG.debug("Time - Interpolation: {0:f}".format(time.time() - tic))

        ipn *= 100
        res = ipn
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
    SUNZ = np.ma.arange(
        NDIM / 2, NDIM + NDIM / 2).reshape(SHAPE) * 60. / float(NDIM)
    SATZ = np.ma.arange(NDIM).reshape(SHAPE) * 60. / float(NDIM)
    AZIDIFF = np.ma.arange(NDIM).reshape(SHAPE) * 179.9 / float(NDIM)
    rfl = this.get_reflectance(SUNZ, SATZ, AZIDIFF, 'M4')
