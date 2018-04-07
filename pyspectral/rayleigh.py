#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2018 Pytroll

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

"""Atmospheric correction of shortwave imager bands in the wavelength range 400
to 800 nm

"""

import logging
import os
from six import integer_types

import h5py
import numpy as np
import dask.array as da
from scipy.interpolate import interpn

from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import (INSTRUMENTS, RAYLEIGH_LUT_DIRS,
                              AEROSOL_TYPES, ATMOSPHERES,
                              BANDNAMES,
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

    """Container for the atmospheric correction of satellite imager short
    wave bands. Removing background contributions of Rayleigh scattering of
    molecules and Mie scattering and absorption by aerosols.

    """

    def __init__(self, platform_name, sensor, **kwargs):
        self.platform_name = platform_name
        self.sensor = sensor
        self.coeff_filename = None

        atm_type = kwargs.get('atmosphere', 'us-standard')
        if atm_type not in ATMOSPHERES:
            raise AttributeError('Atmosphere type not supported! ' +
                                 'Need to be one of {}'.format(str(ATMOSPHERES)))

        aerosol_type = kwargs.get('aerosol_type', 'marine_clean_aerosol')

        if aerosol_type not in AEROSOL_TYPES:
            raise AttributeError('Aerosol type not supported! ' +
                                 'Need to be one of {0}'.format(str(AEROSOL_TYPES)))

        rayleigh_dir = RAYLEIGH_LUT_DIRS[aerosol_type]

        if atm_type not in ATMOSPHERES.keys():
            LOG.error("Atmosphere type %s not supported", atm_type)

        LOG.info("Atmosphere chosen: %s", atm_type)

        # Try fix instrument naming
        instr = INSTRUMENTS.get(platform_name, sensor)
        if instr != sensor:
            sensor = instr
            LOG.warning("Inconsistent sensor/satellite input - " +
                        "sensor set to %s", sensor)

        self.sensor = sensor.replace('/', '')

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
        self._rayl = None
        self._wvl_coord = None
        self._azid_coord = None
        self._satz_sec_coord = None
        self._sunz_sec_coord = None

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
            bandname = BANDNAMES.get(self.sensor, BANDNAMES['generic']).get(bandname, bandname)
        elif isinstance(bandname, (float, integer_types)):
            if not(0.4 < bandname < 0.8):
                raise BandFrequencyOutOfRange(
                    'Requested band frequency should be between 0.4 and 0.8 microns!')
            bandname = get_bandname_from_wavelength(self.sensor, bandname, rsr.rsr)

        wvl, resp = rsr.rsr[bandname][
            'det-1']['wavelength'], rsr.rsr[bandname]['det-1']['response']

        cwvl = get_central_wave(wvl, resp, weight=1. / wvl**4)
        LOG.debug("Band name: %s  Effective wavelength: %f", bandname, cwvl)

        return cwvl

    def get_reflectance_lut(self):
        """Read the LUT with reflectances as a function of wavelength, satellite zenith
        secant, azimuth difference angle, and sun zenith secant

        """
        if self._rayl is None:
            lut_vars = get_reflectance_lut(self.reflectance_lut_filename)
            self._rayl = lut_vars[0]
            # wvl_coord is used in a lot of non-dask functions, keep in memory
            self._wvl_coord = lut_vars[1].persist()
            self._azid_coord = lut_vars[2]
            self._satz_sec_coord = lut_vars[3]
            self._sunz_sec_coord = lut_vars[4]
        return self._rayl, self._wvl_coord, self._azid_coord,\
               self._satz_sec_coord, self._sunz_sec_coord

    def get_reflectance(self, sun_zenith, sat_zenith, azidiff, bandname,
                        redband=None):
        """Get the reflectance from the three sun-sat angles."""
        # Get wavelength in nm for band:
        wvl = self.get_effective_wavelength(bandname) * 1000.0
        rayl, wvl_coord, azid_coord, satz_sec_coord, sunz_sec_coord = self.get_reflectance_lut()
        wvl_coord = wvl_coord.persist()

        clip_angle = da.rad2deg(da.arccos(1. / sunz_sec_coord.max()))
        sun_zenith = da.clip(da.asarray(sun_zenith), 0, clip_angle)
        sunzsec = 1. / da.cos(da.deg2rad(sun_zenith))
        clip_angle = da.rad2deg(da.arccos(1. / satz_sec_coord.max()))
        sat_zenith = da.clip(da.asarray(sat_zenith), 0, clip_angle)
        satzsec = 1. / da.cos(da.deg2rad(da.asarray(sat_zenith)))

        shape = sun_zenith.shape

        if not(wvl_coord.min() < wvl < wvl_coord.max()):
            LOG.warning(
                "Effective wavelength for band %s outside 400-800 nm range!", str(bandname))
            LOG.info(
                "Set the rayleigh/aerosol reflectance contribution to zero!")
            chunks = sun_zenith.chunks if redband is None else redband.chunks
            return da.zeros(shape, chunks=chunks)

        idx = np.searchsorted(wvl_coord, wvl)
        wvl1 = wvl_coord[idx - 1]
        wvl2 = wvl_coord[idx]

        fac = (wvl2 - wvl) / (wvl2 - wvl1)

        # FIXME: Can we do this right before interpolating instead?
        raylwvl = fac * rayl[idx - 1, :, :, :] + (1 - fac) * rayl[idx, :, :, :]

        import time
        tic = time.time()

        if WITH_CYTHON:
            smin = [sunz_sec_coord[0], azid_coord[0], satz_sec_coord[0]]
            smax = [sunz_sec_coord[-1], azid_coord[-1], satz_sec_coord[-1]]
            orders = [
                len(sunz_sec_coord), len(azid_coord), len(satz_sec_coord)]
            minterp = MultilinearInterpolator(smin, smax, orders)

            f_3d_grid = raylwvl
            minterp.set_values(da.atleast_2d(f_3d_grid.ravel()))

            def _do_interp(minterp, sunzsec, azidiff, satzsec):
                interp_points2 = np.vstack((sunzsec.ravel(),
                                            180 - azidiff.ravel(),
                                            satzsec.ravel()))
                res = minterp(interp_points2)
                return res.reshape(sunzsec.shape)

            ipn = da.map_blocks(_do_interp, minterp, sunzsec, azidiff,
                                satzsec, dtype=raylwvl.dtype,
                                chunks=azidiff.chunks)
        else:
            # FIXME: Untested
            def _do_interp(sunz_sec_coord, azid_coord, satz_sec_coord,
                           raylwvl):
                interp_points = np.dstack((sunzsec,
                                           180. - azidiff,
                                           satzsec))

                return interpn((sunz_sec_coord, azid_coord, satz_sec_coord),
                              raylwvl[:, :, :], interp_points)
            ipn = da.map_blocks(_do_interp, sunz_sec_coord, azid_coord, satz_sec_coord,
                                raylwvl[:, :, :], dtype=raylwvl.dtype,
                                chunks=azidiff.chunks)

        LOG.debug("Time - Interpolation: {0:f}".format(time.time() - tic))

        ipn *= 100
        res = ipn
        if redband is not None:
            res = da.where(da.less(redband, 20.), res,
                           (1 - (redband - 20) / 80) * res)

        return da.clip(res, 0, 100)


def get_reflectance_lut(filename):
    """Read the LUT with reflectances as a function of wavelength, satellite
    zenith secant, azimuth difference angle, and sun zenith secant

    """

    h5f = h5py.File(filename, 'r')

    tab = da.from_array(h5f['reflectance'],  chunks=(10, 10, 10, 10))
    wvl = da.from_array(h5f['wavelengths'],  chunks=(100,))
    azidiff = da.from_array(h5f['azimuth_difference'], chunks=(1000,))
    satellite_zenith_secant = da.from_array(h5f['satellite_zenith_secant'], chunks=(1000,))
    sun_zenith_secant = da.from_array(h5f['sun_zenith_secant'], chunks=(1000,))

    return tab, wvl, azidiff, satellite_zenith_secant, sun_zenith_secant

if __name__ == "__main__":
    SHAPE = (1000, 3000)
    NDIM = SHAPE[0] * SHAPE[1]
    SUNZ = np.ma.arange(
        NDIM / 2, NDIM + NDIM / 2).reshape(SHAPE) * 60. / float(NDIM)
    SATZ = np.ma.arange(NDIM).reshape(SHAPE) * 60. / float(NDIM)
    AZIDIFF = np.ma.arange(NDIM).reshape(SHAPE) * 179.9 / float(NDIM)
    rfl = this.get_reflectance(SUNZ, SATZ, AZIDIFF, 'M4')
