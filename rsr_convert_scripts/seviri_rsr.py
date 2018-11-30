#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Copyright (c) 2013-2018 Adam.Dybbroe

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

"""Interface to the SEVIRI spectral response functions for all four MSG
satellites
"""

import os
from xlrd import open_workbook
import numpy as np
from pyspectral.config import get_config
import pkg_resources
import logging

LOG = logging.getLogger(__name__)
DATA_PATH = pkg_resources.resource_filename('pyspectral', 'data/')


class Seviri(object):

    """Class for Seviri RSR"""

    def __init__(self, wavespace='wavelength'):
        """
        Read the seviri relative spectral responses for all channels and all
        MSG satellites.

        Optional input: 'wavespace'. Equals 'wavelength' (units of micron's) on
        default. Can be 'wavenumber' in which case the unit is in cm-1.

        """
        options = get_config()

        self.seviri_path = options['seviri'].get('path')
        if not os.path.exists(self.seviri_path):
            self.seviri_path = os.path.join(
                DATA_PATH, options['seviri'].get('filename'))

        LOG.debug("Original RSR file from EUMETSAT: {}".format(self.seviri_path))

        self.output_dir = options.get('rsr_dir', './')

        self.rsr = None
        self._load()
        self.wavespace = wavespace
        if wavespace not in ['wavelength', 'wavenumber']:
            raise AttributeError("wavespace has to be either " +
                                 "'wavelength' or 'wavenumber'!")

        self.unit = 'micrometer'
        if wavespace == 'wavenumber':
            # Convert to wavenumber:
            self.convert2wavenumber()

        self.central_wavenumber = None
        self.central_wavelength = None

        self.get_centrals()

    def _load(self, filename=None):
        """Read the SEVIRI rsr data"""
        if not filename:
            filename = self.seviri_path

        wb_ = open_workbook(filename)

        self.rsr = {}
        sheet_names = []
        for sheet in wb_.sheets():
            if sheet.name in ['Info', 'Requirements']:
                continue
            ch_name = sheet.name.strip()
            sheet_names.append(sheet.name.strip())

            self.rsr[ch_name] = {'wavelength': None,
                                 'Meteosat-8': None,
                                 'Meteosat-9': None,
                                 'Meteosat-10': None,
                                 'Meteosat-11': None}

            if ch_name.startswith('HRV'):
                wvl = np.array(
                    sheet.col_values(0, start_rowx=37, end_rowx=137))
                # TODO: Add the 'extended' responses as well!
                met8 = np.array(
                    sheet.col_values(1, start_rowx=37, end_rowx=137))
                met9 = np.array(
                    sheet.col_values(3, start_rowx=37, end_rowx=137))
                met10 = np.array(
                    sheet.col_values(5, start_rowx=37, end_rowx=137))
                met11 = np.array(
                    sheet.col_values(6, start_rowx=37, end_rowx=137))
                self.rsr[ch_name]['Meteosat-8'] = met8
                self.rsr[ch_name]['Meteosat-9'] = met9
                self.rsr[ch_name]['Meteosat-10'] = met10
                self.rsr[ch_name]['Meteosat-11'] = met11
            elif ch_name.startswith('IR'):
                wvl = np.array(
                    sheet.col_values(0, start_rowx=13, end_rowx=113))
                met8_95 = np.array(
                    sheet.col_values(1, start_rowx=13, end_rowx=113))
                met9_95 = np.array(
                    sheet.col_values(3, start_rowx=13, end_rowx=113))
                met10_95 = np.array(
                    sheet.col_values(5, start_rowx=13, end_rowx=113))
                met11_95 = np.array(
                    sheet.col_values(7, start_rowx=13, end_rowx=113))
                met8_85 = np.array(
                    sheet.col_values(2, start_rowx=13, end_rowx=113))
                met9_85 = np.array(
                    sheet.col_values(4, start_rowx=13, end_rowx=113))
                met10_85 = np.array(
                    sheet.col_values(6, start_rowx=13, end_rowx=113))
                met11_85 = np.array(
                    sheet.col_values(8, start_rowx=13, end_rowx=113))
                self.rsr[ch_name]['Meteosat-8'] = {'95': met8_95,
                                                   '85': met8_85}
                self.rsr[ch_name]['Meteosat-9'] = {'95': met9_95,
                                                   '85': met9_85}
                self.rsr[ch_name]['Meteosat-10'] = {'95': met10_95,
                                                    '85': met10_85}
                self.rsr[ch_name]['Meteosat-11'] = {'95': met11_95,
                                                    '85': met11_85}
            else:
                wvl = np.array(
                    sheet.col_values(0, start_rowx=12, end_rowx=112))
                met8 = np.array(
                    sheet.col_values(1, start_rowx=12, end_rowx=112))
                met9 = np.array(
                    sheet.col_values(2, start_rowx=12, end_rowx=112))
                met10 = np.array(
                    sheet.col_values(3, start_rowx=12, end_rowx=112))
                met11 = np.array(
                    sheet.col_values(4, start_rowx=12, end_rowx=112))
                self.rsr[ch_name]['Meteosat-8'] = met8
                self.rsr[ch_name]['Meteosat-9'] = met9
                self.rsr[ch_name]['Meteosat-10'] = met10
                self.rsr[ch_name]['Meteosat-11'] = met11

            self.rsr[ch_name]['wavelength'] = wvl

    def convert2wavenumber(self):
        """Convert from wavelengths to wavenumber"""
        for chname in self.rsr.keys():
            elems = [k for k in self.rsr[chname].keys()]
            for sat in elems:
                if sat == "wavelength":
                    LOG.debug("Get the wavenumber from the wavelength: sat=%s chname=%s", sat, chname)
                    wnum = 1. / (1e-4 * self.rsr[chname][sat][:])  # microns to cm
                    self.rsr[chname]['wavenumber'] = wnum[::-1]
                else:
                    if type(self.rsr[chname][sat]) is dict:
                        for name in self.rsr[chname][sat].keys():
                            resp = self.rsr[chname][sat][name][:]
                            self.rsr[chname][sat][name] = resp[::-1]
                    else:
                        resp = self.rsr[chname][sat][:]
                        self.rsr[chname][sat] = resp[::-1]

        for chname in self.rsr.keys():
            del self.rsr[chname]['wavelength']

        self.unit = 'cm-1'

    def get_centrals(self):
        """Get the central wavenumbers or central wavelengths of all channels,
        depending on the given 'wavespace'
        """
        result = {}
        for chname in self.rsr.keys():
            result[chname] = {}
            if self.wavespace == "wavelength":
                x__ = self.rsr[chname]["wavelength"]
            else:
                x__ = self.rsr[chname]["wavenumber"]
            for sat in self.rsr[chname].keys():
                if sat in ["wavelength", "wavenumber"]:
                    continue
                if type(self.rsr[chname][sat]) is dict:
                    result[chname][sat] = {}
                    for name in self.rsr[chname][sat].keys():
                        resp = self.rsr[chname][sat][name]
                        result[chname][sat][name] = get_central_wave(x__, resp)
                else:
                    resp = self.rsr[chname][sat]
                    result[chname][sat] = get_central_wave(x__, resp)

        if self.wavespace == "wavelength":
            self.central_wavelength = result
        else:
            self.central_wavenumber = result


def get_central_wave(wavl, resp):
    """Calculate the central wavelength or the central wavenumber,
    depending on what is input
    """
    return np.trapz(resp * wavl, wavl) / np.trapz(resp, wavl)


def generate_seviri_file(seviri, platform_name):
    """Generate the pyspectral internal common format relative response
    function file for one SEVIRI
    """
    import h5py

    filename = os.path.join(seviri.output_dir,
                            "rsr_seviri_{0}.h5".format(platform_name))

    sat_name = platform_name
    with h5py.File(filename, "w") as h5f:

        h5f.attrs['description'] = 'Relative Spectral Responses for SEVIRI'
        h5f.attrs['platform_name'] = platform_name
        bandlist = [str(key) for key in seviri.rsr.keys()]
        h5f.attrs['band_names'] = bandlist

        for key in seviri.rsr.keys():
            grp = h5f.create_group(key)
            if isinstance(seviri.central_wavelength[key][sat_name], dict):
                grp.attrs['central_wavelength'] = \
                    seviri.central_wavelength[key][sat_name]['95']
            else:
                grp.attrs['central_wavelength'] = \
                    seviri.central_wavelength[key][sat_name]
            arr = seviri.rsr[key]['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = 1e-06
            dset[...] = arr
            try:
                arr = seviri.rsr[key][sat_name]['95']
            except ValueError:
                arr = seviri.rsr[key][sat_name]
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr

    return


def main():
    """Main"""
    sev_obj = Seviri()

    for satnum in [8, 9, 10, 11]:
        generate_seviri_file(sev_obj, 'Meteosat-{0:d}'.format(satnum))
        print("Meteosat-{0:d} done...".format(satnum))


if __name__ == "__main__":
    main()
