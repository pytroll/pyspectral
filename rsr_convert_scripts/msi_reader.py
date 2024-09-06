#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2022 Pytroll developers
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

"""Reading the original agency formattet Sentinel-2 MSI relative spectral responses.

See:

https://earth.esa.int/documents/247904/685211/S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.0.xlsx

"""

import logging
import os

import pandas as pd
import numpy as np

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

MSI_BAND_NAMES = {"B01": "B1",
                  "B02": "B2",
                  "B03": "B3",
                  "B04": "B4",
                  "B05": "B5",
                  "B06": "B6",
                  "B07": "B7",
                  "B08": "B8",
                  "B8A": "B8A",
                  "B09": "B9",
                  "B10": "B10",
                  "B11": "B11",
                  "B12": "B12"}

SHEET_HEADERS = {"S2A": "Spectral Responses (S2A)",
                 "S2B": "Spectral Responses (S2B)",
                 "S2C": "Spectral Responses (S2C)"}

PLATFORM_SHORT_NAME = {"Sentinel-2A": "S2A",
                       "Sentinel-2B": "S2B",
                       "Sentinel-2C": "S2C"}


class MsiRSR(InstrumentRSR):
    """Class for Sentinel-2 MSI RSR."""

    def __init__(self, bandname, platform_name):
        """Read the Sentinel-2 MSI relative spectral responses for all channels."""
        super(MsiRSR, self).__init__(bandname, platform_name)

        self.instrument = "msi"
        self.platform_name = platform_name
        self.short_plat = PLATFORM_SHORT_NAME[platform_name]
        self._get_options_from_config()

        LOG.debug(f"Filename: {self.path}")
        if os.path.exists(self.path):
            self._load(platform_name)
        else:
            raise IOError(f"Couldn't find an existing file for this band: {str(self.bandname)}")

    def _load(self, scale=0.001):
        """Load the Sentinel-2 MSI relative spectral responses."""
        bname = MSI_BAND_NAMES.get(self.bandname)
        df = pd.read_excel(self.path, engine='openpyxl', sheet_name=SHEET_HEADERS[self.short_plat])
        wvl = np.array(df['SR_WL'])
        resp = np.array(df[f"{self.short_plat}_SR_AV_{bname}"])

        mask = np.less_equal(resp, 0.00001)
        wvl0 = np.ma.masked_array(wvl, mask=mask)
        wvl_mask = np.ma.masked_outside(wvl, wvl0.min() - 2, wvl0.max() + 2)

        wvl = wvl_mask.compressed()
        resp = np.ma.masked_array(resp, mask=wvl_mask.mask).compressed()
        self.rsr = {"wavelength": wvl / 1000., "response": resp}


if __name__ == "__main__":

    for plat_name in ["Sentinel-2A", "Sentinel-2B", "Sentinel-2C"]:
        tohdf5(MsiRSR, plat_name, sorted(MSI_BAND_NAMES))
