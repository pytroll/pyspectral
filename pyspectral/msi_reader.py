#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

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

"""
Reading the original agency formattet Sentinel-2 MSI relative spectral responses

https://earth.esa.int/documents/247904/685211/S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.0.xlsx

"""


import os
from xlrd import open_workbook
import numpy as np
from pyspectral.utils import convert2hdf5 as tohdf5

import logging
LOG = logging.getLogger(__name__)

from pyspectral.config import get_config
from pyspectral.raw_reader import InstrumentRSR

MSI_BAND_NAMES = {}
MSI_BAND_NAMES['S2A'] = {'S2A_SR_AV_B1': 'ch1',
                         'S2A_SR_AV_B2': 'ch2',
                         'S2A_SR_AV_B3': 'ch3',
                         'S2A_SR_AV_B4': 'ch4',
                         'S2A_SR_AV_B5': 'ch5',
                         'S2A_SR_AV_B6': 'ch6',
                         'S2A_SR_AV_B7': 'ch7',
                         'S2A_SR_AV_B8': 'ch8',
                         'S2A_SR_AV_B8A': 'ch9',
                         'S2A_SR_AV_B9': 'ch10',
                         'S2A_SR_AV_B10': 'ch11',
                         'S2A_SR_AV_B11': 'ch12',
                         'S2A_SR_AV_B12': 'ch13'}
MSI_BAND_NAMES['S2B'] = {'S2B_SR_AV_B1': 'ch1',
                         'S2B_SR_AV_B2': 'ch2',
                         'S2B_SR_AV_B3': 'ch3',
                         'S2B_SR_AV_B4': 'ch4',
                         'S2B_SR_AV_B5': 'ch5',
                         'S2B_SR_AV_B6': 'ch6',
                         'S2B_SR_AV_B7': 'ch7',
                         'S2B_SR_AV_B8': 'ch8',
                         'S2B_SR_AV_B8A': 'ch9',
                         'S2B_SR_AV_B9': 'ch10',
                         'S2B_SR_AV_B10': 'ch11',
                         'S2B_SR_AV_B11': 'ch12',
                         'S2B_SR_AV_B12': 'ch13'}

SHEET_HEADERS = {'Spectral Responses (S2A)': 'S2A',
                 'Spectral Responses (S2B)': 'S2B'}

PLATFORM_SHORT_NAME = {'Sentinel-2A': 'S2A',
                       'Sentinel-2B': 'S2B'}


class MsiRSR(InstrumentRSR):

    """Class for Sentinel-2 MSI RSR"""

    def __init__(self, bandname, platform_name):
        """
        Read the Sentinel-2 MSI relative spectral responses for all channels.

        """
        super(MsiRSR, self).__init__(bandname, platform_name)

        self.instrument = 'msi'
        self._get_options_from_config()

        LOG.debug("Filename: %s", str(self.path))
        if os.path.exists(self.path):
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, scale=0.001):
        """Load the Sentinel-2 MSI relative spectral responses
        """

        with open_workbook(self.path) as wb_:
            for sheet in wb_.sheets():
                if sheet.name not in SHEET_HEADERS.keys():
                    continue

                plt_short_name = PLATFORM_SHORT_NAME.get(self.platform_name)
                if plt_short_name != SHEET_HEADERS.get(sheet.name):
                    continue

                wvl = sheet.col_values(0, 1)
                for idx in range(1, sheet.row_len(0)):
                    ch_name = MSI_BAND_NAMES[plt_short_name].get(str(sheet.col_values(idx, 0, 1)[0]))
                    if ch_name != self.bandname:
                        continue

                    resp = sheet.col_values(idx, 1)

                self.rsr = {'wavelength': np.array(wvl) / 1000.,
                            'response': np.array(resp)}
                break


def main():
    """Main"""
    bands = MSI_BAND_NAMES['S2A'].values()
    bands.sort()
    for platform_name in ['Sentinel-2A', ]:
        tohdf5(MsiRSR, platform_name, bands)

    bands = MSI_BAND_NAMES['S2B'].values()
    bands.sort()
    for platform_name in ['Sentinel-2B', ]:
        tohdf5(MsiRSR, platform_name, bands)


if __name__ == "__main__":
    main()
