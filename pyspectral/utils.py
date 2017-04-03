#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015, 2016, 2017 Adam.Dybbroe

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

"""Utility functions"""

import os
from os.path import expanduser

import numpy as np

from pyspectral import get_config

BANDNAMES = {'VIS006': 'VIS0.6',
             'VIS008': 'VIS0.8',
             'IR_016': 'NIR1.6',
             'IR_039': 'IR3.9',
             'WV_062': 'IR6.2',
             'WV_073': 'IR7.3',
             'IR_087': 'IR8.7',
             'IR_097': 'IR9.7',
             'IR_108': 'IR10.8',
             'IR_120': 'IR12.0',
             'IR_134': 'IR13.4',
             'HRV': 'HRV'
             }

INSTRUMENTS = {'NOAA-19': 'avhrr/3',
               'NOAA-18': 'avhrr/3',
               'NOAA-17': 'avhrr/3',
               'NOAA-16': 'avhrr/3',
               'NOAA-15': 'avhrr/3',
               'NOAA-14': 'avhrr/2',
               'NOAA-12': 'avhrr/2',
               'NOAA-11': 'avhrr/2',
               'NOAA-9': 'avhrr/2',
               'NOAA-7': 'avhrr/2',
               'NOAA-10': 'avhrr/1',
               'NOAA-8': 'avhrr/1',
               'NOAA-6': 'avhrr/1',
               'TIROS-N': 'avhrr/1',
               'Metop-A': 'avhrr/3',
               'Metop-B': 'avhrr/3',
               'Metop-C': 'avhrr/3'
               }


HTTP_PYSPECTRAL_RSR = "https://dl.dropboxusercontent.com/u/37482654/pyspectral_rsr_data.tgz"
HTTP_RAYLEIGH_ONLY_LUTS = "https://dl.dropboxusercontent.com/u/37482654/rayleigh_only/rayleigh_luts_rayleigh_only.tgz"
HTTP_RURAL_AEROSOL_LUTS = "https://dl.dropboxusercontent.com/u/37482654/rural_aerosol/rayleigh_luts_rural_aerosol.tgz"


OPTIONS = {}
CONF = get_config()
for option, value in CONF.items('general', raw=True):
    OPTIONS[option] = value

LOCAL_RSR_DIR = expanduser(OPTIONS['rsr_dir'])
try:
    os.makedirs(LOCAL_RSR_DIR)
except OSError:
    if not os.path.isdir(LOCAL_RSR_DIR):
        raise

LOCAL_RAYLEIGH_DIR = expanduser(OPTIONS['rayleigh_dir'])

HTTPS = [HTTP_RAYLEIGH_ONLY_LUTS, HTTP_RURAL_AEROSOL_LUTS]
RAYLEIGH_SUB_NAMES = ['rayleigh_only', 'rural_aerosol']
RAYLEIGH_LUT_DIRS = {}
for http_addr, sub_dir_name in zip(HTTPS, RAYLEIGH_SUB_NAMES):
    dirname = os.path.join(LOCAL_RAYLEIGH_DIR, sub_dir_name)
    try:
        os.makedirs(dirname)
    except OSError:
        if not os.path.isdir(dirname):
            raise

    RAYLEIGH_LUT_DIRS[sub_dir_name] = dirname


def convert2wavenumber(rsr):
    """Take rsr data set with all channels and detectors for an instrument
    each with a set of wavelengths and normalised responses and
    convert to wavenumbers and responses
    """
    retv = {}
    for chname in rsr.keys():  # Go through bands/channels
        retv[chname] = {}
        for det in rsr[chname].keys():  # Go through detectors
            retv[chname][det] = {}
            for sat in rsr[chname][det].keys():
                if sat == "wavelength":
                    # micro meters to cm
                    wnum = 1. / (1e-4 * rsr[chname][det][sat])
                    retv[chname][det]['wavenumber'] = wnum[::-1]
                elif sat == "response":
                    # Flip the response array:
                    if type(rsr[chname][det][sat]) is dict:
                        retv[chname][det][sat] = {}
                        for name in rsr[chname][det][sat].keys():
                            resp = rsr[chname][det][sat][name]
                            retv[chname][det][sat][name] = resp[::-1]
                    else:
                        resp = rsr[chname][det][sat]
                        retv[chname][det][sat] = resp[::-1]

    unit = 'cm-1'
    si_scale = 100.0

    return retv, {'unit': unit, 'si_scale': si_scale}


def get_central_wave(wav, resp, weight=1.0):
    """Calculate the central wavelength or the central wavenumber, depending on
    which parameters is input.  On default the weighting funcion is
    f(lambda)=1.0, but it is possible to add a custom weight, e.g. f(lambda) =
    1./lambda**4 for Rayleigh scattering calculations

    """

    # info: {'unit': unit, 'si_scale': si_scale}
    # To get the wavelenght/wavenumber in SI units (m or m-1):
    # wav = wav * info['si_scale']

    # res = np.trapz(resp*wav, wav) / np.trapz(resp, wav)
    # Check if it is a wavelength or a wavenumber and convert to microns or cm-1:
    # This should perhaps be user defined!?
    # if info['unit'].find('-1') > 0:
    # Wavenumber:
    #     res *=

    return np.trapz(resp * wav * weight, wav) / np.trapz(resp * weight, wav)


def get_bandname_from_wavelength(wavelength, rsr, epsilon=0.1):
    """Get the bandname from h5 rsr provided the approximate wavelength."""
    # channel_list = [channel for channel in rsr.rsr if abs(
    # rsr.rsr[channel]['det-1']['central_wavelength'] - wavelength) < epsilon]

    chdist_min = 2.0
    chfound = None
    for channel in rsr:
        chdist = abs(
            rsr[channel]['det-1']['central_wavelength'] - wavelength)
        if chdist < chdist_min and chdist < epsilon:
            chdist_min = chdist
            chfound = channel

    return BANDNAMES.get(chfound, chfound)


def sort_data(x_vals, y_vals):
    """Sort the data so that x is monotonically increasing and contains
    no duplicates.
    """
    # Sort data
    idxs = np.argsort(x_vals)
    x_vals = x_vals[idxs]
    y_vals = y_vals[idxs]

    # De-duplicate data
    mask = np.r_[True, (np.diff(x_vals) > 0)]
    if not mask.all():
        # what is this for?
        numof_duplicates = np.repeat(mask, np.equal(mask, False)).shape[0]
        del numof_duplicates
    x_vals = x_vals[mask]
    y_vals = y_vals[mask]

    return x_vals, y_vals


def convert2hdf5(ClassIn, platform_name, bandnames, scale=1e-06):
    """Retrieve original RSR data and convert to internal hdf5 format.

    *scale* is the number which has to be multiplied to the wavelength data in
    order to get it in the SI unit meter

    """
    import h5py

    instr = ClassIn(bandnames[0], platform_name)
    instr_name = instr.instrument.replace('/', '')
    filename = os.path.join(instr.output_dir,
                            "rsr_%s_%s.h5" % (instr_name,
                                              platform_name))

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = ('Relative Spectral Responses for ' +
                                    instr.instrument.upper())
        h5f.attrs['platform_name'] = platform_name
        h5f.attrs['band_names'] = bandnames

        for chname in bandnames:
            sensor = ClassIn(chname, platform_name)
            grp = h5f.create_group(chname)
            wvl = sensor.rsr['wavelength'][~np.isnan(sensor.rsr['wavelength'])]
            rsp = sensor.rsr['response'][~np.isnan(sensor.rsr['wavelength'])]
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = sensor.rsr['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = scale
            dset[...] = arr
            arr = sensor.rsr['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr


def get_rayleigh_reflectance(parms, azidiff, sunz, satz):
    """Get the Rayleigh reflectance applying the polynomial fit parameters

    P(x,y) = c_{00} + c_{10}x + ...+ c_{n0}x^n +
             c_{01}y + ...+ c_{0n}y^n +
             c_{11}xy + c_{12}xy^2 + ... +
             c_{1(n-1)}xy^{n-1}+ ... + c_{(n-1)1}x^{n-1}y

    x = relative azimuth difference angle:
        Azimuth difference   0: Instrument is looking into Sun
        Azimuth difference 180: Instrument and Sun are looking in the same
        direction
    y = secant of the satellite zenith angle

    NB! The azimuth difference provided here is defined as described in the
    documentation, and differs by 180 degrees to the angle x required in the
    polynomial fit.

    """

    sec = 1. / np.cos(np.deg2rad(satz))
    sunsec = 1. / np.cos(np.deg2rad(sunz))

    coeffs = [[parms[:, 0], parms[:, 1], parms[:, 2], parms[:, 3], parms[:, 4], parms[:, 5]],
              [parms[:, 6], parms[:, 11], parms[:, 15],
                  parms[:, 18], parms[:, 20]],
              [parms[:, 7], parms[:, 12], parms[:, 16], parms[:, 19]],
              [parms[:, 8], parms[:, 13], parms[:, 17]],
              [parms[:, 9], parms[:, 14]],
              [parms[:, 10]]
              ]

    # The RTM simulations are based on a definition of the sun-satellite azimuth
    # difference according to the following:
    # Azimuth difference 0: Instrument is looking into Sun
    # Azimuth difference 180: Instrument and Sun are looking in the same
    # direction
    indices = np.rint(180. - azidiff).astype('i')

    res = 0

    for line, cols in enumerate(coeffs):
        for col, coeff in enumerate(cols):
            factor = coeff[indices]
            for i in range(line):
                factor *= sec
            for i in range(col):
                factor *= sunsec
            res += factor

    return res


def download_rsr():
    """Download the pre-compiled hdf5 formatet relative spectral response functions
    from the internet

    """

    #
    import tarfile
    import requests
    from tqdm import tqdm

    response = requests.get(HTTP_PYSPECTRAL_RSR)
    filename = os.path.join(LOCAL_RSR_DIR, "pyspectral_rsr_data.tgz")
    with open(filename, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)

    tar = tarfile.open(filename)
    tar.extractall(LOCAL_RSR_DIR)
    tar.close()
    os.remove(filename)


def download_luts():
    """Download the luts from internet."""
    #
    import tarfile
    import requests
    from tqdm import tqdm

    for http, subname in zip(HTTPS, RAYLEIGH_SUB_NAMES):
        response = requests.get(http)

        subdirname = RAYLEIGH_LUT_DIRS[subname]
        filename = os.path.join(subdirname, "rayleigh_luts_%s.tgz" % subname)
        with open(filename, "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)

        tar = tarfile.open(filename)
        tar.extractall(subdirname)
        tar.close()
        os.remove(filename)
