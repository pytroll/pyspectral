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
from pyspectral.raw_reader import InstrumentRSR
import logging
LOG = logging.getLogger(__name__)


MSI_BAND_NAMES = {}
MSI_BAND_NAMES['S2A'] = {'S2A_SR_AV_B1': 'B01',
                         'S2A_SR_AV_B2': 'B02',
                         'S2A_SR_AV_B3': 'B03',
                         'S2A_SR_AV_B4': 'B04',
                         'S2A_SR_AV_B5': 'B05',
                         'S2A_SR_AV_B6': 'B06',
                         'S2A_SR_AV_B7': 'B07',
                         'S2A_SR_AV_B8': 'B08',
                         'S2A_SR_AV_B8A': 'B8A',
                         'S2A_SR_AV_B9': 'B09',
                         'S2A_SR_AV_B10': 'B10',
                         'S2A_SR_AV_B11': 'B11',
                         'S2A_SR_AV_B12': 'B12'}
MSI_BAND_NAMES['S2B'] = {'S2B_SR_AV_B1': 'B01',
                         'S2B_SR_AV_B2': 'B02',
                         'S2B_SR_AV_B3': 'B03',
                         'S2B_SR_AV_B4': 'B04',
                         'S2B_SR_AV_B5': 'B05',
                         'S2B_SR_AV_B6': 'B06',
                         'S2B_SR_AV_B7': 'B07',
                         'S2B_SR_AV_B8': 'B08',
                         'S2B_SR_AV_B8A': 'B8A',
                         'S2B_SR_AV_B9': 'B09',
                         'S2B_SR_AV_B10': 'B10',
                         'S2B_SR_AV_B11': 'B11',
                         'S2B_SR_AV_B12': 'B12'}

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
                    resp = np.array(resp)
                    resp = np.where(resp == '', 0, resp).astype('float32')
                    mask = np.less_equal(resp, 0.00001)
                    wvl0 = np.ma.masked_array(wvl, mask=mask)
                    wvl_mask = np.ma.masked_outside(wvl, wvl0.min() - 2, wvl0.max() + 2)

                    wvl = wvl_mask.compressed()
                    resp = np.ma.masked_array(resp, mask=wvl_mask.mask).compressed()
                    self.rsr = {'wavelength': wvl / 1000., 'response': resp}

                    break

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
