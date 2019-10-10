#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2019 Adam.Dybbroe

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

"""Planck radiation equation."""

import numpy as np
import logging

try:
    import dask.array as da
except ImportError:
    da = np

LOG = logging.getLogger(__name__)

H_PLANCK = 6.62606957 * 1e-34  # SI-unit = [J*s]
K_BOLTZMANN = 1.3806488 * 1e-23  # SI-unit = [J/K]
C_SPEED = 2.99792458 * 1e8  # SI-unit = [m/s]

EPSILON = 0.000001


def blackbody_rad2temp(wavelength, radiance):
    """Derive brightness temperatures from radiance using the Planck function.

    Wavelength space. Assumes SI units as input and returns
    temperature in Kelvin

    """
    mask = False
    if np.isscalar(radiance):
        rad = np.array([radiance, ], dtype='float64')
    else:
        rad = np.array(radiance, dtype='float64')
        if np.ma.is_masked(radiance):
            mask = radiance.mask

    rad = np.ma.masked_array(rad, mask=mask)
    rad = np.ma.masked_less_equal(rad, 0)

    if np.isscalar(wavelength):
        wvl = np.array([wavelength, ], dtype='float64')
    else:
        wvl = np.array(wavelength, dtype='float64')

    const1 = H_PLANCK * C_SPEED / K_BOLTZMANN
    const2 = 2 * H_PLANCK * C_SPEED**2
    res = const1 / (wvl * np.log(np.divide(const2, rad * wvl**5) + 1.0))

    shape = rad.shape
    resshape = res.shape

    if wvl.shape[0] == 1:
        if rad.shape[0] == 1:
            return res[0]
        else:
            return res[::].reshape(shape)
    else:
        if rad.shape[0] == 1:
            return res[0, :]
        else:
            if len(shape) == 1:
                return np.reshape(res, (shape[0], resshape[1]))
            else:
                return np.reshape(res, (shape[0], shape[1], resshape[1]))


def blackbody_wn_rad2temp(wavenumber, radiance):
    """Derive brightness temperatures from radiance using the Planck function.

    Wavenumber space

    """
    if np.isscalar(radiance):
        radiance = np.array([radiance], dtype='float64')
    elif isinstance(radiance, (list, tuple)):
        radiance = np.array(radiance, dtype='float64')
    if np.isscalar(wavenumber):
        wavnum = np.array([wavenumber], dtype='float64')
    elif isinstance(wavenumber, (list, tuple)):
        wavnum = np.array(wavenumber, dtype='float64')

    const1 = H_PLANCK * C_SPEED / K_BOLTZMANN
    const2 = 2 * H_PLANCK * C_SPEED**2
    res = const1 * wavnum / np.log(
        np.divide(const2 * wavnum**3, radiance) + 1.0)

    shape = radiance.shape
    resshape = res.shape

    if wavnum.shape[0] == 1:
        if radiance.shape[0] == 1:
            return res[0]
        else:
            return res[::].reshape(shape)
    else:
        if radiance.shape[0] == 1:
            return res[0, :]
        else:
            if len(shape) == 1:
                return res.reshape((shape[0], resshape[1]))
            else:
                return res.reshape((shape[0], shape[1], resshape[1]))


def planck(wave, temperature, wavelength=True):
    """Derive the Planck radiation as a function of wavelength or wavenumber.

    SI units.
    _planck(wave, temperature, wavelength=True)
    wave = Wavelength/wavenumber or a sequence of wavelengths/wavenumbers (m or m^-1)
    temp = Temperature (scalar) or a sequence of temperatures (K)


    Output: Wavelength space: The spectral radiance per meter (not micron!)
            Unit = W/m^2 sr^-1 m^-1

            Wavenumber space: The spectral radiance in Watts per square meter
            per steradian per m-1:
            Unit = W/m^2 sr^-1 (m^-1)^-1 = W/m sr^-1

            Converting from SI units to mW/m^2 sr^-1 (cm^-1)^-1:
            1.0 W/m^2 sr^-1 (m^-1)^-1 = 0.1 mW/m^2 sr^-1 (cm^-1)^-1

    """
    units = ['wavelengths', 'wavenumbers']
    if wavelength:
        LOG.debug("Using {0} when calculating the Blackbody radiance".format(
            units[(wavelength is True) - 1]))

    if np.isscalar(temperature):
        temperature = np.array([temperature, ], dtype='float64')
    elif isinstance(temperature, (list, tuple)):
        temperature = np.array(temperature, dtype='float64')

    shape = temperature.shape
    if np.isscalar(wave):
        wln = np.array([wave, ], dtype='float64')
    else:
        wln = np.array(wave, dtype='float64')

    if wavelength:
        const = 2 * H_PLANCK * C_SPEED ** 2
        nom = const / wln ** 5
        arg1 = H_PLANCK * C_SPEED / (K_BOLTZMANN * wln)
    else:
        nom = 2 * H_PLANCK * (C_SPEED ** 2) * (wln ** 3)
        arg1 = H_PLANCK * C_SPEED * wln / K_BOLTZMANN

    with np.errstate(divide='ignore', invalid='ignore'):
        # use dask functions when needed
        np_ = np if isinstance(temperature, np.ndarray) else da
        arg2 = np_.where(np_.greater(np.abs(temperature), EPSILON),
                         np_.divide(1., temperature), np.nan).reshape(-1, 1)

    if isinstance(arg2, np.ndarray):
        # don't compute min/max if we have dask arrays
        LOG.debug("Max and min - arg1: %s  %s",
                  str(np.nanmax(arg1)), str(np.nanmin(arg1)))
        LOG.debug("Max and min - arg2: %s  %s",
                  str(np.nanmax(arg2)), str(np.nanmin(arg2)))

    try:
        exp_arg = np.multiply(arg1.astype('float64'), arg2.astype('float64'))
    except MemoryError:
        LOG.warning(("Dimensions used in numpy.multiply probably reached "
                     "limit!\n"
                     "Make sure the Radiance<->Tb table has been created "
                     "and try running again"))
        raise

    if isinstance(exp_arg, np.ndarray) and exp_arg.min() < 0:
        LOG.debug("Max and min before exp: %s  %s",
                  str(exp_arg.max()), str(exp_arg.min()))
        LOG.warning("Something is fishy: \n" +
                    "\tDenominator might be zero or negative in radiance derivation:")
        dubious = np.where(exp_arg < 0)[0]
        LOG.warning(
            "Number of items having dubious values: " + str(dubious.shape[0]))

    with np.errstate(over='ignore'):
        denom = np.exp(exp_arg) - 1
        rad = nom / denom
        radshape = rad.shape
        if wln.shape[0] == 1:
            if temperature.shape[0] == 1:
                return rad[0, 0]
            else:
                return rad[:, 0].reshape(shape)
        else:
            if temperature.shape[0] == 1:
                return rad[0, :]
            else:
                if len(shape) == 1:
                    return rad.reshape((shape[0], radshape[1]))
                else:
                    return rad.reshape((shape[0], shape[1], radshape[1]))


def blackbody_wn(wavenumber, temp):
    """Derive the Planck radiation as a function of wavenumber.

    SI units.
    blackbody_wn(wavnum, temperature)
    wavenumber = A wavenumber (scalar) or a sequence of wave numbers (m-1)
    temp = A temperatfure (scalar) or a sequence of temperatures (K)

    Output: The spectral radiance in Watts per square meter per steradian
            per m-1:
            Unit = W/m^2 sr^-1 (m^-1)^-1 = W/m sr^-1

            Converting from SI units to mW/m^2 sr^-1 (cm^-1)^-1:
            1.0 W/m^2 sr^-1 (m^-1)^-1 = 0.1 mW/m^2 sr^-1 (cm^-1)^-1

    """
    return planck(wavenumber, temp, wavelength=False)


def blackbody(wavel, temp):
    """Derive the Planck radiation as a function of wavelength.

    SI units.
    blackbody(wavelength, temperature)
    wavel = Wavelength or a sequence of wavelengths (m)
    temp = Temperature (scalar) or a sequence of temperatures (K)

    Output: The spectral radiance per meter (not micron!)
            Unit = W/m^2 sr^-1 m^-1

    """
    return planck(wavel, temp, wavelength=True)
