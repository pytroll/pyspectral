#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2022 Pytroll developers
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Atmospheric correction of shortwave imager bands in the wavelength range 400 to 800 nm."""

import logging
import numbers
import os

import h5py
import numpy as np

try:
    import dask.array as da
except ImportError:
    da = None

from geotiepoints.multilinear import MultilinearInterpolator

from pyspectral.config import get_config
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import (
    AEROSOL_TYPES,
    ATM_CORRECTION_LUT_VERSION,
    ATMOSPHERES,
    BANDNAMES,
    INSTRUMENTS,
    download_luts,
    get_central_wave,
    get_rayleigh_lut_dir,
)

LOG = logging.getLogger(__name__)


def _map_blocks_or_direct_call(func, *args, **kwargs):
    """Call dask's map_blocks or call func directly if dask is not available."""
    if da is None:
        kwargs.pop("meta", None)
        kwargs.pop("dtype", None)
        kwargs.pop("chunks", None)
        return func(*args, **kwargs)
    return da.map_blocks(func, *args, **kwargs)


def _clip_angles_inside_coordinate_range(zenith_angle, zenith_secant_max):
    """Clipping solar- or satellite zenith angles to be inside the allowed coordinate range.

    The "allowed" coordinate range is 0 to the angle corresponiding to a
    maximum secant. The maximum secant is here the maximum available in the
    Rayleigh LUT file.

    Also the nan's in the angle array are filled with zeros (0)!

    """
    clip_angle = np.nan_to_num(np.rad2deg(np.arccos(1. / zenith_secant_max)))
    zang = np.nan_to_num(zenith_angle)
    return np.clip(zang, 0, clip_angle)


class RayleighConfigBaseClass(object):
    """A base class for the Atmospheric correction, handling the configuration and LUT download."""

    def __init__(self, aerosol_type, atm_type='us-standard'):
        """Initialize class and determine LUT to use."""
        options = get_config()
        self.do_download = 'download_from_internet' in options and options['download_from_internet']
        self._lutfiles_version_uptodate = False

        if atm_type not in ATMOSPHERES:
            raise AttributeError('Atmosphere type not supported! ' +
                                 'Need to be one of {}'.format(str(ATMOSPHERES)))

        self._aerosol_type = aerosol_type
        if aerosol_type not in AEROSOL_TYPES:
            raise AttributeError('Aerosol type not supported! ' +
                                 'Need to be one of {0}'.format(str(AEROSOL_TYPES)))

        if atm_type not in ATMOSPHERES.keys():
            LOG.error("Atmosphere type %s not supported", atm_type)

        LOG.info("Atmosphere chosen: %s", atm_type)

        if (self._aerosol_type in ATM_CORRECTION_LUT_VERSION and
                self._get_lutfiles_version() == ATM_CORRECTION_LUT_VERSION[self._aerosol_type]['version']):
            self.lutfiles_version_uptodate = True

    def _get_lutfiles_version(self):
        """Get LUT file version.

        Check the version of the atm correction luts from the version file in the
        specific aerosol correction directory.

        """
        basedir = get_rayleigh_lut_dir(self._aerosol_type)
        lutfiles_version_path = os.path.join(basedir,
                                             ATM_CORRECTION_LUT_VERSION[self._aerosol_type]['filename'])

        if not os.path.exists(lutfiles_version_path):
            return "v0.0.0"

        with open(lutfiles_version_path, 'r') as fpt:
            # Get the version from the file
            return fpt.readline().strip()

    @property
    def lutfiles_version_uptodate(self):
        """Tell whether LUT file is up to date or not."""
        return self._lutfiles_version_uptodate

    @lutfiles_version_uptodate.setter
    def lutfiles_version_uptodate(self, value):
        """Store whether LUT file is up to date or not."""
        self._lutfiles_version_uptodate = value


class Rayleigh(RayleighConfigBaseClass):
    """
    Container for the atmospheric correction of satellite imager bands.

    This class removes background contributions of Rayleigh scattering of
    molecules and Mie scattering and absorption by aerosols.

    """

    def __init__(self, platform_name, sensor, **kwargs):
        """Initialize class and determine LUT to use."""
        atm_type = kwargs.get('atmosphere', 'us-standard')
        aerosol_type = kwargs.get('aerosol_type', 'marine_clean_aerosol')

        super(Rayleigh, self).__init__(aerosol_type, atm_type)

        self.platform_name = platform_name
        self.sensor = sensor
        self.coeff_filename = None

        # Try to fix instrument naming
        instr = INSTRUMENTS.get(platform_name, sensor)
        if instr != sensor:
            if isinstance(instr, list):
                if sensor not in instr:
                    raise ValueError("This satellite has multiple sensors, you must explicitly state which to use.")
            else:
                sensor = instr
                LOG.warning("Inconsistent sensor/satellite input - " +
                            "sensor set to %s", sensor)

        self.sensor = sensor.replace('/', '')

        rayleigh_dir = get_rayleigh_lut_dir(aerosol_type)
        ext = atm_type.replace(' ', '_')
        lutname = "rayleigh_lut_{0}.h5".format(ext)
        self.reflectance_lut_filename = os.path.join(rayleigh_dir, lutname)

        if not self._lutfiles_version_uptodate and self.do_download:
            LOG.info("Will download from internet...")
            download_luts(aerosol_types=[aerosol_type])

        if (not os.path.exists(self.reflectance_lut_filename) or
                not os.path.isfile(self.reflectance_lut_filename)):
            raise IOError('pyspectral file for Rayleigh scattering correction ' +
                          'does not exist! Filename = ' +
                          str(self.reflectance_lut_filename))

        LOG.debug('LUT filename: %s', str(self.reflectance_lut_filename))

    def _get_effective_wavelength_and_band_name(self, band_name_or_wavelength):
        """Get the effective wavelength in nanometers and name of the band/channel.

        The provided argument can be either the name of a band/channel that
        pyspectral knows about in its RSR files or it can be a wavelength
        specified in micrometers. If a wavelength is provided it is converted
        to nanometers and returned. If a band name is provided then it is used
        to lookup the spectral response and determine an effective wavelength
        useful for rayleigh correction.

        Returns:
            A two element tuple of (wavelength in nanometers, name of band). If
            a wavelength is provided then the band name is a string
            representation of the wavelength.

        """
        # Get wavelength in nm for band:
        if isinstance(band_name_or_wavelength, numbers.Real):
            LOG.warning('A wavelength is provided instead of band name - ' +
                        'disregard the relative spectral responses and assume ' +
                        'it is the effective wavelength: %f (micro meter)', band_name_or_wavelength)
            wvl = band_name_or_wavelength
            band_name = f'{wvl:f}um'
        else:
            band_name = band_name_or_wavelength
            wvl = _get_rsr_wavelength_from_band_name(
                self.platform_name,
                self.sensor,
                band_name,
            )
            band_name_map = BANDNAMES.get(self.sensor, BANDNAMES['generic'])
            band_name_or_wavelength = band_name_map.get(band_name, band_name)
        LOG.debug("Band name: %s  Effective wavelength: %fum", band_name_or_wavelength, wvl)
        return wvl * 1000.0, band_name

    @staticmethod
    def _interp_rayleigh_refl_by_angles(sun_zenith, sat_zenith, azidiff,
                                        rayleigh_refl, reflectance_lut_filename):
        azid_coord, satz_sec_coord, sunz_sec_coord = get_reflectance_lut_from_file(
            reflectance_lut_filename)
        azid_coord = azid_coord.astype(rayleigh_refl.dtype, copy=False)
        satz_sec_coord = satz_sec_coord.astype(rayleigh_refl.dtype, copy=False)
        sunz_sec_coord = sunz_sec_coord.astype(rayleigh_refl.dtype, copy=False)

        sun_zenith = _clip_angles_inside_coordinate_range(sun_zenith, sunz_sec_coord.max())
        sunzsec = 1. / np.cos(np.deg2rad(sun_zenith))

        sat_zenith = _clip_angles_inside_coordinate_range(sat_zenith, satz_sec_coord.max())
        satzsec = 1. / np.cos(np.deg2rad(sat_zenith))

        smin = [sunz_sec_coord[0], azid_coord[0], satz_sec_coord[0]]
        smax = [sunz_sec_coord[-1], azid_coord[-1], satz_sec_coord[-1]]
        orders = [len(sunz_sec_coord), len(azid_coord), len(satz_sec_coord)]
        f_3d_grid = np.atleast_2d(rayleigh_refl.ravel())

        minterp = MultilinearInterpolator(smin, smax, orders, dtype=rayleigh_refl.dtype)
        minterp.set_values(f_3d_grid)
        interp_points2 = np.vstack((sunzsec.ravel(), 180 - azidiff.ravel(), satzsec.ravel()))
        res = minterp(interp_points2)
        res *= 100
        return res.reshape(sunzsec.shape)

    def get_reflectance(self, sun_zenith, sat_zenith, azidiff,
                        band_name_or_wavelength, redband=None):
        """Get the reflectance from the three sun-sat angles."""
        # if the user gave us non-dask arrays we'll use the dask
        # version of the algorithm but return numpy arrays back
        compute = da is not None and not isinstance(sun_zenith, da.Array)

        wvl, band_name = self._get_effective_wavelength_and_band_name(band_name_or_wavelength)
        repr_arr = sun_zenith if redband is None else redband
        try:
            rayleigh_refl = _get_wavelength_adjusted_lut_rayleigh_reflectance(
                self.reflectance_lut_filename, wvl)
        except ValueError:
            LOG.warning("Effective wavelength for band %s outside "
                        "nominal 400-800 nm range!", str(band_name))
            LOG.info("Setting the rayleigh/aerosol reflectance contribution to zero!")
            zeros_like = np.zeros_like if isinstance(repr_arr, np.ndarray) else da.zeros_like
            res = zeros_like(repr_arr)
        else:
            rayleigh_refl = rayleigh_refl.astype(repr_arr.dtype, copy=False)
            res = _map_blocks_or_direct_call(self._interp_rayleigh_refl_by_angles,
                                             sun_zenith, sat_zenith, azidiff, rayleigh_refl,
                                             self.reflectance_lut_filename,
                                             meta=np.array((), dtype=repr_arr.dtype),
                                             dtype=repr_arr.dtype,
                                             chunks=getattr(azidiff, "chunks", None))

        if redband is not None:
            res = _map_blocks_or_direct_call(self._relax_rayleigh_refl_correction_where_cloudy,
                                             redband, res,
                                             meta=np.array((), dtype=res.dtype),
                                             dtype=res.dtype,
                                             chunks=getattr(res, "chunks", None))

        res = np.clip(res, 0, 100)
        if compute:
            res = res.compute()
        return res

    @staticmethod
    def _relax_rayleigh_refl_correction_where_cloudy(redband, rayleigh_refl):
        return np.where(redband < 20., rayleigh_refl,
                        (1 - (redband - 20) / 80) * rayleigh_refl)

    @staticmethod
    def reduce_rayleigh_highzenith(zenith, rayref, thresh_zen, maxzen, strength):
        """Reduce the Rayleigh correction amount at high zenith angles.

        This linearly scales the Rayleigh reflectance, `rayref`, for solar or satellite zenith angles, `zenith`,
        above a threshold angle, `thresh_zen`. Between `thresh_zen` and `maxzen` the Rayleigh reflectance will
        be linearly scaled, from one at `thresh_zen` to zero at `maxzen`.
        """
        LOG.info("Reducing Rayleigh effect at high zenith angles.")
        factor = 1. - strength * np.where(zenith < thresh_zen, 0, (zenith - thresh_zen) / (maxzen - thresh_zen))
        # For low zenith factor can be greater than one, so we need to clip it into a sensible range.
        factor = np.clip(factor, 0, 1)
        return rayref * factor


def _get_rsr_wavelength_from_band_name(platform_name, sensor, band_name):
    try:
        rsr = RelativeSpectralResponse(platform_name, sensor)
    except OSError:
        LOG.exception(
            "No spectral responses for this platform and sensor: %s %s", platform_name, sensor)
        msg = ("Can't get effective wavelength for band %s on platform %s and sensor %s" %
               (str(band_name), platform_name, sensor))
        raise KeyError(msg)

    wvl = rsr.rsr[band_name]['det-1']['wavelength']
    resp = rsr.rsr[band_name]['det-1']['response']
    cwvl = get_central_wave(wvl, resp, weight=1. / wvl**4)
    return cwvl


def _get_wavelength_adjusted_lut_rayleigh_reflectance(lut_filename, wvl):
    with h5py.File(lut_filename, 'r') as h5f:
        rayleigh_refl = h5f["reflectance"]
        wvl_coord = h5f["wavelengths"][:]
        if not wvl_coord.min() < wvl < wvl_coord.max():
            raise ValueError("Wavelength out of range for available LUT wavelengths")
        wavelength_index, wavelength_factor = _get_wavelength_index_and_factor(wvl_coord, wvl)
        raylwvl = (wavelength_factor * rayleigh_refl[wavelength_index - 1, :, :, :] +
                   (1 - wavelength_factor) * rayleigh_refl[wavelength_index, :, :, :])
    return raylwvl


def _get_wavelength_index_and_factor(wvl_coord, wvl):
    wavelength_index = np.searchsorted(wvl_coord, wvl)
    wvl1 = wvl_coord[wavelength_index - 1]
    wvl2 = wvl_coord[wavelength_index]
    wavelength_factor = (wvl2 - wvl) / (wvl2 - wvl1)
    return wavelength_index, wavelength_factor


def get_reflectance_lut_from_file(lut_filename):
    """Get reflectance LUT.

    Read the Look-Up Tables from file with reflectances as a function of
    wavelength, satellite zenith secant, azimuth difference angle, and sun
    zenith secant.

    """
    with h5py.File(lut_filename, 'r') as h5f:
        azidiff = h5f['azimuth_difference']
        satellite_zenith_secant = h5f['satellite_zenith_secant']
        sun_zenith_secant = h5f['sun_zenith_secant']

        # load all of the data we are going to use in to memory
        azidiff = azidiff[:]
        satellite_zenith_secant = satellite_zenith_secant[:]
        sun_zenith_secant = sun_zenith_secant[:]

    return azidiff, satellite_zenith_secant, sun_zenith_secant


def check_and_download(dry_run=False, aerosol_types=None):
    """Download atm correction LUT tables if they are not up-to-date already.

    Do a check for the version of the atmospheric correction LUTs and attempt
    downloading only if needed.

    """
    aerosol_types = aerosol_types or AEROSOL_TYPES
    needed_aerosol_types = []
    for aerosol_type in aerosol_types:
        atmcorr = RayleighConfigBaseClass(aerosol_type)
        if atmcorr.lutfiles_version_uptodate:
            LOG.info("Atm correction LUTs, for aerosol distribution %s, already the latest!",
                     aerosol_type)
        else:
            needed_aerosol_types.append(aerosol_type)

    # Download
    if needed_aerosol_types:
        download_luts(aerosol_types=needed_aerosol_types, dry_run=dry_run)
