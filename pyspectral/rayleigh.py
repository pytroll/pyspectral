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
import os
import time
import logging
from six import integer_types

import h5py
import numpy as np

try:
    from dask.array import (where, zeros, clip, rad2deg, deg2rad, cos, arccos,
                            atleast_2d, Array, map_blocks, from_array)
    import dask.array as da
    HAVE_DASK = True
    # try:
    #     # use serializable h5py wrapper to make sure files are closed properly
    #     import h5pickle as h5py
    # except ImportError:
    #     pass
except ImportError:
    from numpy import where, zeros, clip, rad2deg, deg2rad, cos, arccos, atleast_2d
    da = None
    map_blocks = None
    from_array = None
    Array = None
    HAVE_DASK = False

from geotiepoints.multilinear import MultilinearInterpolator
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import (INSTRUMENTS, RAYLEIGH_LUT_DIRS,
                              AEROSOL_TYPES, ATMOSPHERES,
                              BANDNAMES,
                              ATM_CORRECTION_LUT_VERSION,
                              download_luts, get_central_wave,
                              get_bandname_from_wavelength)

from pyspectral.config import get_config

LOG = logging.getLogger(__name__)


class BandFrequencyOutOfRange(ValueError):
    """Exception when the band frequency is out of the visible range"""

    pass


class Rayleigh(object):
    """Container for the atmospheric correction of satellite imager bands.

    This class removes background contributions of Rayleigh scattering of
    molecules and Mie scattering and absorption by aerosols.

    """

    def __init__(self, platform_name, sensor, **kwargs):
        """Initialize class and determine LUT to use."""
        self.platform_name = platform_name
        self.sensor = sensor
        self.coeff_filename = None
        options = get_config()
        self.do_download = False
        self._lutfiles_version_uptodate = False

        atm_type = kwargs.get('atmosphere', 'us-standard')
        if atm_type not in ATMOSPHERES:
            raise AttributeError('Atmosphere type not supported! ' +
                                 'Need to be one of {}'.format(str(ATMOSPHERES)))

        aerosol_type = kwargs.get('aerosol_type', 'marine_clean_aerosol')
        self._aerosol_type = aerosol_type

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

        if 'download_from_internet' in options and options['download_from_internet']:
            self.do_download = True

        if (self._aerosol_type in ATM_CORRECTION_LUT_VERSION and
                self._get_lutfiles_version() == ATM_CORRECTION_LUT_VERSION[self._aerosol_type]['version']):
            self._lutfiles_version_uptodate = True

        ext = atm_type.replace(' ', '_')
        lutname = "rayleigh_lut_{0}.h5".format(ext)
        self.reflectance_lut_filename = os.path.join(rayleigh_dir, lutname)

        if not self._lutfiles_version_uptodate and self.do_download:
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

    def _get_lutfiles_version(self):
        """Check the version of the atm correction luts from the version file in the
           specific aerosol correction directory

        """
        basedir = RAYLEIGH_LUT_DIRS[self._aerosol_type]
        lutfiles_version_path = os.path.join(basedir,
                                             ATM_CORRECTION_LUT_VERSION[self._aerosol_type]['filename'])

        if not os.path.exists(lutfiles_version_path):
            return "v0.0.0"

        with open(lutfiles_version_path, 'r') as fpt:
            # Get the version from the file
            return fpt.readline().strip()

    def get_effective_wavelength(self, bandname):
        """Get the effective wavelength with Rayleigh scattering in mind"""
        try:
            rsr = RelativeSpectralResponse(self.platform_name, self.sensor)
        except(IOError, OSError):
            LOG.exception(
                "No spectral responses for this platform and sensor: %s %s", self.platform_name, self.sensor)
            if isinstance(bandname, (float, integer_types)):
                LOG.warning(
                    "Effective wavelength is set to the requested band wavelength = %f", bandname)
                return bandname
            return None

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
            self._wvl_coord = lut_vars[1]
            self._azid_coord = lut_vars[2]
            self._satz_sec_coord = lut_vars[3]
            self._sunz_sec_coord = lut_vars[4]
        return self._rayl, self._wvl_coord, self._azid_coord,\
            self._satz_sec_coord, self._sunz_sec_coord

    def get_reflectance(self, sun_zenith, sat_zenith, azidiff, bandname, redband=None):
        """Get the reflectance from the three sun-sat angles"""
        # Get wavelength in nm for band:
        if isinstance(bandname, float):
            LOG.warning('A wavelength is provided instead of band name - ' +
                        'disregard the relative spectral responses and assume ' +
                        'it is the effective wavelength: %f (micro meter)', bandname)
            wvl = bandname * 1000.0
        else:
            wvl = self.get_effective_wavelength(bandname)
            if wvl is None:
                LOG.error("Can't get effective wavelength for band %s on platform %s and sensor %s",
                          str(bandname), self.platform_name, self.sensor)
                return None
            else:
                wvl = wvl * 1000.0

        rayl, wvl_coord, azid_coord, satz_sec_coord, sunz_sec_coord = \
            self.get_reflectance_lut()

        # force dask arrays
        compute = False
        if HAVE_DASK and not isinstance(sun_zenith, Array):
            compute = True
            sun_zenith = from_array(sun_zenith, chunks=sun_zenith.shape)
            sat_zenith = from_array(sat_zenith, chunks=sat_zenith.shape)
            azidiff = from_array(azidiff, chunks=azidiff.shape)
            if redband is not None:
                redband = from_array(redband, chunks=redband.shape)

        clip_angle = rad2deg(arccos(1. / sunz_sec_coord.max()))
        sun_zenith = clip(sun_zenith, 0, clip_angle)
        sunzsec = 1. / cos(deg2rad(sun_zenith))
        clip_angle = rad2deg(arccos(1. / satz_sec_coord.max()))
        sat_zenith = clip(sat_zenith, 0, clip_angle)
        satzsec = 1. / cos(deg2rad(sat_zenith))
        shape = sun_zenith.shape

        if not(wvl_coord.min() < wvl < wvl_coord.max()):
            LOG.warning(
                "Effective wavelength for band %s outside 400-800 nm range!",
                str(bandname))
            LOG.info(
                "Set the rayleigh/aerosol reflectance contribution to zero!")
            if HAVE_DASK:
                chunks = sun_zenith.chunks if redband is None \
                    else redband.chunks
                res = zeros(shape, chunks=chunks)
                return res.compute() if compute else res
            else:
                return zeros(shape)

        idx = np.searchsorted(wvl_coord, wvl)
        wvl1 = wvl_coord[idx - 1]
        wvl2 = wvl_coord[idx]

        fac = (wvl2 - wvl) / (wvl2 - wvl1)
        raylwvl = fac * rayl[idx - 1, :, :, :] + (1 - fac) * rayl[idx, :, :, :]
        tic = time.time()

        smin = [sunz_sec_coord[0], azid_coord[0], satz_sec_coord[0]]
        smax = [sunz_sec_coord[-1], azid_coord[-1], satz_sec_coord[-1]]
        orders = [
            len(sunz_sec_coord), len(azid_coord), len(satz_sec_coord)]
        f_3d_grid = atleast_2d(raylwvl.ravel())

        if HAVE_DASK and isinstance(smin[0], Array):
            # compute all of these at the same time before passing to the interpolator
            # otherwise they are computed separately
            smin, smax, orders, f_3d_grid = da.compute(smin, smax, orders, f_3d_grid)
        minterp = MultilinearInterpolator(smin, smax, orders)
        minterp.set_values(f_3d_grid)

        def _do_interp(minterp, sunzsec, azidiff, satzsec):
            interp_points2 = np.vstack((sunzsec.ravel(),
                                        180 - azidiff.ravel(),
                                        satzsec.ravel()))
            res = minterp(interp_points2)
            return res.reshape(sunzsec.shape)

        if HAVE_DASK:
            ipn = map_blocks(_do_interp, minterp, sunzsec, azidiff,
                             satzsec, dtype=raylwvl.dtype,
                             chunks=azidiff.chunks)
        else:
            ipn = _do_interp(minterp, sunzsec, azidiff, satzsec)

        LOG.debug("Time - Interpolation: {0:f}".format(time.time() - tic))

        ipn *= 100
        res = ipn
        if redband is not None:
            res = where(redband < 20., res,
                        (1 - (redband - 20) / 80) * res)

        res = clip(res, 0, 100)
        if compute:
            res = res.compute()
        return res


def get_reflectance_lut(filename):
    """Read the LUT with reflectances as a function of wavelength, satellite
    zenith secant, azimuth difference angle, and sun zenith secant

    """

    h5f = h5py.File(filename, 'r')

    tab = h5f['reflectance']
    wvl = h5f['wavelengths']
    azidiff = h5f['azimuth_difference']
    satellite_zenith_secant = h5f['satellite_zenith_secant']
    sun_zenith_secant = h5f['sun_zenith_secant']

    if HAVE_DASK:
        tab = from_array(tab, chunks=(10, 10, 10, 10))
        wvl = wvl[:]  # no benefit to dask-ifying this
        azidiff = from_array(azidiff, chunks=(1000,))
        satellite_zenith_secant = from_array(satellite_zenith_secant,
                                             chunks=(1000,))
        sun_zenith_secant = from_array(sun_zenith_secant,
                                       chunks=(1000,))
    else:
        # load all of the data we are going to use in to memory
        tab = tab[:]
        wvl = wvl[:]
        azidiff = azidiff[:]
        satellite_zenith_secant = satellite_zenith_secant[:]
        sun_zenith_secant = sun_zenith_secant[:]
        h5f.close()

    return tab, wvl, azidiff, satellite_zenith_secant, sun_zenith_secant
