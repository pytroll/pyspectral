#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017 Adam.Dybbroe

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

"""Read the Himawari AHI spectral response functions. Data from
http://www.data.jma.go.jp/mscweb/en/himawari89/space_segment/spsg_ahi.html#srf

"""

import logging
LOG = logging.getLogger(__name__)

import os
import numpy as np
from xlrd import open_workbook

from pyspectral.utils import get_central_wave
from pyspectral.config import get_config


AHI_BAND_NAMES = {'Band 1': 'ch1',
                  'Band 2': 'ch2',
                  'Band 3': 'ch3',
                  'Band 4': 'ch4',
                  'Band 5': 'ch5',
                  'Band 6': 'ch6',
                  'Band 7': 'ch7',
                  'Band 8': 'ch8',
                  'Band 9': 'ch9',
                  'Band 10': 'ch10',
                  'Band 11': 'ch11',
                  'Band 12': 'ch12',
                  'Band 13': 'ch13',
                  'Band 14': 'ch14',
                  'Band 15': 'ch15',
                  'Band 16': 'ch16'
                  }

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class AhiRSR(object):

    """Container for the Himawari AHI relative spectral response data"""

    def __init__(self, platform_name, wavespace='wavelength'):
        """
        """
        self.platform_name = platform_name
        self.filename = None
        self.rsr = None

        options = get_config()

        self.output_dir = options.get('rsr_dir', './')
        ahi_options = options[platform_name + '-ahi']
        self.filename = ahi_options['path']
        LOG.debug("Filenames: " + str(self.filename))
        if os.path.exists(self.filename):
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, filename=None):
        """Load the Himawari AHI RSR data for the band requested
        """
        if not filename:
            filename = self.filename

        wb_ = open_workbook(filename)
        self.rsr = {}
        sheet_names = []
        for sheet in wb_.sheets():
            if sheet.name in ['Title', ]:
                continue
            ch_name = AHI_BAND_NAMES.get(
                sheet.name.strip(), sheet.name.strip())
            sheet_names.append(sheet.name.strip())
            self.rsr[ch_name] = {'wavelength': None,
                                 'response': None}
            wvl = np.array(
                sheet.col_values(0, start_rowx=5, end_rowx=5453))
            resp = np.array(
                sheet.col_values(2, start_rowx=5, end_rowx=5453))
            self.rsr[ch_name]['wavelength'] = wvl
            self.rsr[ch_name]['response'] = resp


def convert2hdf5(platform_name):
    """Retrieve original RSR data and convert to internal hdf5 format"""

    import h5py

    ahi = AhiRSR(platform_name)
    filename = os.path.join(ahi.output_dir,
                            "rsr_ahi_{platform}.h5".format(platform=platform_name))

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for AHI'
        h5f.attrs['platform_name'] = platform_name
        h5f.attrs['sensor'] = 'ahi'
        h5f.attrs['band_names'] = AHI_BAND_NAMES.values()

        for chname in AHI_BAND_NAMES.values():

            grp = h5f.create_group(chname)
            wvl = ahi.rsr[chname][
                'wavelength'][~np.isnan(ahi.rsr[chname]['wavelength'])]
            rsp = ahi.rsr[chname][
                'response'][~np.isnan(ahi.rsr[chname]['wavelength'])]
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = ahi.rsr[chname]['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = 1e-06
            dset[...] = arr
            arr = ahi.rsr[chname]['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr


def main():
    """Main"""

    for satnum in [8, 9]:
        convert2hdf5('Himawari-{0:d}'.format(satnum))
        print("Himawari-{0:d} done...".format(satnum))

if __name__ == "__main__":

    import sys
    LOG = logging.getLogger('ahi_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    main()
