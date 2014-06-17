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

"""Interface to the SEVIRI spectral response functions for all four MSG
satellites
"""

import logging
LOG = logging.getLogger(__name__)

import ConfigParser
import os

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")

from xlrd import open_workbook
import numpy as np

METEOSAT_SAT = {'meteosat10': 'met10',
                'meteosat9': 'met9',
                'meteosat8': 'met8',
                'meteosat11': 'met11',
                }


class Seviri(object):

    def __init__(self, wavespace='wavelength'):
        """
        Read the seviri relative spectral responses for all channels and all
        MSG satellites.

        Optional input: 'wavespace'. Equals 'wavelength' (units of micron's) on
        default. Can be 'wavenumber' in which case the unit is in cm-1.

        """

        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception(
                'Failed reading configuration file: ' + str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items('seviri', raw=True):
            options[option] = value

        self.seviri_path = options.get('path')

        for option, value in conf.items('general', raw=True):
            options[option] = value

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

        wb = open_workbook(filename)

        self.rsr = {}
        sheet_names = []
        for sheet in wb.sheets():
            if sheet.name in ['Info', 'Requirements']:
                continue
            ch_name = sheet.name.strip()
            sheet_names.append(sheet.name.strip())

            self.rsr[ch_name] = {'wavelength': None,
                                 'met8': None,
                                 'met9': None,
                                 'met10': None,
                                 'met11': None}

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
                self.rsr[ch_name]['met8'] = met8
                self.rsr[ch_name]['met9'] = met9
                self.rsr[ch_name]['met10'] = met10
                self.rsr[ch_name]['met11'] = met11
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
                self.rsr[ch_name]['met8'] = {'95': met8_95, '85': met8_85}
                self.rsr[ch_name]['met9'] = {'95': met9_95, '85': met9_85}
                self.rsr[ch_name]['met10'] = {'95': met10_95, '85': met10_85}
                self.rsr[ch_name]['met11'] = {'95': met11_95, '85': met11_85}
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
                self.rsr[ch_name]['met8'] = met8
                self.rsr[ch_name]['met9'] = met9
                self.rsr[ch_name]['met10'] = met10
                self.rsr[ch_name]['met11'] = met11

            self.rsr[ch_name]['wavelength'] = wvl

    def convert2wavenumber(self):
        """Convert from wavelengths to wavenumber"""

        for chname in self.rsr.keys():
            for sat in self.rsr[chname].keys():
                if sat == "wavelength":
                    wnum = 1. / (1e-4 * self.rsr[chname][sat])  # microns to cm
                    self.rsr[chname]['wavenumber'] = wnum[::-1]
                    del self.rsr[chname][sat]
                else:
                    if type(self.rsr[chname][sat]) is dict:
                        for name in self.rsr[chname][sat].keys():
                            resp = self.rsr[chname][sat][name]
                            self.rsr[chname][sat][name] = resp[::-1]
                    else:
                        resp = self.rsr[chname][sat]
                        self.rsr[chname][sat] = resp[::-1]

        self.unit = 'cm-1'

    def get_centrals(self):
        """Get the central wavenumbers or central wavelengths of all channels,
        depending on the given 'wavespace'"""

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
    """Calculate the central wavelength or the central wavenumber, depending on
    what is input"""

    return np.trapz(resp * wavl, wavl) / np.trapz(resp, wavl)


def generate_seviri_file(seviri, platform_id, sat_number):
    """Generate the pyspectral internal common format relative response
    function file for one SEVIRI"""

    filename = os.path.join(sevObj.output_dir,
                            "rsr_seviri_%s%d.h5" % (platform_id, sat_number))

    sat_name = METEOSAT_SAT['%s%d' % (platform_id, sat_number)]
    with h5py.File(filename, "w") as h5f:

        h5f.attrs['description'] = 'Relative Spectral Responses for SEVIRI'
        h5f.attrs['platform'] = platform_id
        h5f.attrs['sat_number'] = sat_number
        bandlist = [str(key) for key in seviri.rsr.keys()]
        h5f.attrs['band_names'] = bandlist

        for key in seviri.rsr.keys():
            grp = h5f.create_group(key)
            if isinstance(seviri.central_wavelength[key][sat_name], dict):
                grp.attrs['central_wavelength'] = seviri.central_wavelength[
                    key][sat_name]['95']
            else:
                grp.attrs['central_wavelength'] = seviri.central_wavelength[
                    key][sat_name]
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

if __name__ == "__main__":
    sevObj = Seviri()

    import h5py
    for satnum in [8, 9, 10, 11]:
        generate_seviri_file(sevObj, 'meteosat', satnum)
        print "meteosat%d done..." % satnum
