#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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

"""Planck radiation equation
"""

import numpy as np

h_planck = 6.62606957*1e-34 # SI-unit = [J*s]
k_boltzmann = 1.3806488*1e-23 # SI-unit = [J/K]
c_speed = 2.99792458*1e8 # SI-unit = [m/s]

EPSILON = 0.000001

# -------------------------------------------------------------------
def blackbody_wn(wavnum, temperature):
    """The Planck radiation or Blackbody radiation as a function of wave number
    SI units!
    blackbody_wn(wavnum, temperature)
    wavnum = Array of wave numbers (m-1)
    temperature = Array of temperatures (K)

    Output: The spectral radiance in Watts per square meter per steradian
            per m-1:
            Unit = W/m^2 sr^-1 (m^-1)^-1 = W/m sr^-1

            Converting from SI units to mW/m^2 sr^-1 (cm^-1)^-1:
            1.0 W/m^2 sr^-1 (m^-1)^-1 = 0.1 mW/m^2 sr^-1 (cm^-1)^-1
    """

    if np.isscalar(temperature):
        temperature = [temperature, ]
    temperature = np.array(temperature, dtype='float64')
    shape = temperature.shape
    if np.isscalar(wavnum):
        wavnum = [wavnum,]
    wavnum = np.array(wavnum, dtype='float64')

    wnpow3 = wavnum*wavnum*wavnum
    nom = 2 * h_planck * c_speed * c_speed * wnpow3
    arg1 = h_planck * c_speed * wavnum / k_boltzmann
    arg2 = np.where(np.greater(np.abs(temperature), EPSILON), 
                    np.array(1. / temperature), -9).reshape(-1, 1)

    arg2 = np.ma.masked_array(arg2, mask = arg2==-9)
    exp_arg = np.multiply(arg1.astype('float32'), arg2.astype('float32'))
    denom = np.exp(exp_arg) - 1

    rad = nom / denom
    radshape = rad.shape
    if wavnum.shape[0] == 1:
        if temperature.shape[0] == 1:
            return rad[0, 0]
        else:
            return rad[:, 0].reshape(shape)
    else:
        if temperature.shape[0] == 1:
            return rad[0, :]
        else:
            if len(shape) == 1:
                return np.reshape(rad, (shape[0], radshape[1]))
            else:
                return np.reshape(rad, (shape[0], shape[1], radshape[1]))

# -------------------------------------------------------------------
def blackbody(wl, temperature):
    """The Planck radiation or Blackbody radiation as a function of wavelength
    SI units.
    blackbody(wl, temperature)
    wl = Array of wavelengths (m)
    temperature = Array of temperatures (K)

    Output: The spectral radiance per meter (not micron!)
            Unit = W/m^2 sr^-1 m^-1
    """

    if np.isscalar(temperature):
        temperature = [temperature, ]
    temperature = np.array(temperature, dtype='float64')
    shape = temperature.shape
    #print("temperature min and max = " + str(temperature.min()) + 
    #      " " + str(temperature.max()))
    if np.isscalar(wl):
        wl = [wl,]
    wl = np.array(wl, dtype='float64')

    const = 2 * h_planck * c_speed * c_speed
    wlpow5 = wl*wl*wl*wl*wl
    nom = const / wlpow5
    arg1 = h_planck*c_speed / (k_boltzmann * wl)
    arg2 = np.where(np.greater(np.abs(temperature), EPSILON), 
                    np.array(1. / temperature), -9).reshape(-1, 1)
    arg2 = np.ma.masked_array(arg2, mask = arg2==-9)
    #print("Max and min - arg1: " + str(arg1.max()) + '   ' + str(arg1.min()))
    #print("Max and min - arg2: " + str(arg2.max()) + '   ' + str(arg2.min()))
    exp_arg = np.multiply(arg1.astype('float32'), arg2.astype('float32'))
    #print("Max and min before exp: " + str(exp_arg.max()) + 
    #      ' ' + str(exp_arg.min()))
    denom = np.exp(exp_arg) - 1

    rad = nom / denom
    #print "rad.shape = ", rad.shape
    radshape = rad.shape
    if wl.shape[0] == 1:
        if temperature.shape[0] == 1:
            return rad[0, 0]
        else:
            return rad[:, 0].reshape(shape)
    else:
        if temperature.shape[0] == 1:
            return rad[0, :]
        else:
            if len(shape) == 1:
                return np.reshape(rad, (shape[0], radshape[1]))
            else:
                return np.reshape(rad, (shape[0], shape[1], radshape[1]))
