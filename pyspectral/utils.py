#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015, 2016 Adam.Dybbroe

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

import numpy as np

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
                else:
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
    import os.path

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
            aatsr = ClassIn(chname, platform_name)
            grp = h5f.create_group(chname)
            wvl = aatsr.rsr['wavelength'][~np.isnan(aatsr.rsr['wavelength'])]
            rsp = aatsr.rsr['response'][~np.isnan(aatsr.rsr['wavelength'])]
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = aatsr.rsr['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = scale
            dset[...] = arr
            arr = aatsr.rsr['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr
