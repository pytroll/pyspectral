#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2023 Pytroll developers
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

"""Planck radiation equation."""

import logging

import numpy as np

try:
    import dask.array as da
except ImportError:
    da = np

from pyspectral.utils import use_map_blocks_on

LOG = logging.getLogger(__name__)

H_PLANCK = 6.62606957 * 1e-34  # SI-unit = [J*s]
K_BOLTZMANN = 1.3806488 * 1e-23  # SI-unit = [J/K]
C_SPEED = 2.99792458 * 1e8  # SI-unit = [m/s]

PLANCK_C1 = H_PLANCK * C_SPEED / K_BOLTZMANN
PLANCK_C2 = 2 * H_PLANCK * C_SPEED**2

EPSILON = 0.000001


@use_map_blocks_on("radiance")
def blackbody_rad2temp(wavelength, radiance):
    """Derive brightness temperatures from radiance using the inverse Planck function.

    Args:
        wavelength: The wavelength to use, in SI units (metre).
        radiance: The radiance to derive temperatures from, in SI units (W/m^2 sr^-1). Scalar or arrays are accepted.

    Returns:
        The derived temperature in Kelvin.

    """
    if getattr(wavelength, "dtype", None) != radiance.dtype:
        # avoid a wavelength numpy scalar upcasting radiances (ex. 32-bit to 64-bit float)
        wavelength = radiance.dtype.type(wavelength)
    with np.errstate(divide='ignore', invalid='ignore'):
        return PLANCK_C1 / (wavelength * np.log(PLANCK_C2 / (radiance * wavelength**5) + 1.0))


@use_map_blocks_on("radiance")
def blackbody_wn_rad2temp(wavenumber, radiance):
    """Derive brightness temperatures from radiance using the inverse Planck function.

    Args:
        wavenumber: The wavenumber to use, in SI units (1/metre).
        radiance: The radiance to derive temperatures from, in SI units (W/m^2 sr^-1). Scalar or arrays are accepted.

    Returns:
        The derived temperature in Kelvin.

    """
    with np.errstate(divide='ignore', invalid='ignore'):
        return PLANCK_C1 * wavenumber / np.log((PLANCK_C2 * wavenumber**3) / radiance + 1.0)


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
            1.0 W/m^2 sr^-1 (m^-1)^-1 = 1.0e5 mW/m^2 sr^-1 (cm^-1)^-1

    """
    units = ['wavelengths', 'wavenumbers']
    if wavelength:
        LOG.debug("Using {0} when calculating the Blackbody radiance".format(
            units[(wavelength is True) - 1]))

    if wavelength:
        nom = PLANCK_C2 / wave ** 5
        arg1 = PLANCK_C1 / wave
    else:
        nom = PLANCK_C2 * wave ** 3
        arg1 = PLANCK_C1 * wave

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
        exp_arg = np.multiply(arg1, arg2)
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
        return nom / denom


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
            1.0 W/m^2 sr^-1 (m^-1)^-1 = 1.0e5 mW/m^2 sr^-1 (cm^-1)^-1

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
