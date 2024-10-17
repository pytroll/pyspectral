#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2024 Pytroll developers
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

"""Landsat-8/9 OLI/TIRS reader.
This reader generates spectral responses for OLI and TIRS instruments aboard Landsat-8 and -9.
We assume that the instruments are one combined instrument from the user perspective, called `oli_tirs` rather
than generating RSRs for the two instruments separately.
The original spectral response data can be found at the links below.
Landsat-8/OLI:    https://landsat.gsfc.nasa.gov/wp-content/uploads/2014/09/Ball_BA_RSR.v1.2.xlsx
Landsat-9/OLI-2:  https://landsat.gsfc.nasa.gov/wp-content/uploads/2024/03/L9_OLI2_Ball_BA_RSR.v2-1.xlsx
Landsat-8/TIRS:   https://landsat.gsfc.nasa.gov/wp-content/uploads/2013/06/TIRS_Relative_Spectral_Responses.BA_.v1.xlsx
Landsat-9/TIRS-2: https://landsat.gsfc.nasa.gov/wp-content/uploads/2021-10/L9_TIRS2_Relative_Spectral_Responses.BA.v1.0.xlsx
"""

import logging
import os

import numpy as np
import pandas as pd

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

OLI_BAND_NAMES = {"B1": "CoastalAerosol",
                  "B2": "Blue",
                  "B3": "Green",
                  "B4": "Red",
                  "B5": "NIR",
                  "B6": "Cirrus",
                  "B7": "SWIR1",
                  "B8": "SWIR2",
                  "B9": "Pan"}

TIRS_SHEETNAMES_L8 = {"B10": "TIRS BA RSR",
                      "B11": "TIRS BA RSR"}
TIRS_BAND_NAMES_L8 = {"B10": "TIRS1 10.8um band average",
                      "B11": "TIRS2 12.0um band average"}

TIRS_SHEETNAMES_L9 = {"B10": "TIRS Band 10 BA RSR",
                      "B11": "TIRS Band 11 BA RSR"}
TIRS_BAND_NAMES_L9 = {"B10": "Band 10 Band=Average RSR",
                      "B11": "Band 11 Band-Average RSR"}


class OliRSR(InstrumentRSR):
    """Class for Landsat OLI RSR."""

    def __init__(self, bandname, platform_name):
        """Read the Landsat OLI relative spectral responses for all channels."""
        super(OliRSR, self).__init__(bandname, platform_name)
        self.instrument = "oli_tirs"
        self._get_options_from_config()
        self.band = bandname
        opts = self.options[f"{platform_name}-{self.instrument}"]
        if bandname in OLI_BAND_NAMES:
            self.path = opts["path"] + opts["oli"]
        elif bandname in TIRS_BAND_NAMES_L8:
            self.path = opts["path"] + opts["tirs"]
        else:
            raise ValueError(f"Unknown band name: {bandname}")

        LOG.debug(f"Filename: {self.path}")
        if os.path.exists(self.path):
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, scale=0.001):
        """Load the Landsat OLI relative spectral responses."""
        if self.band in OLI_BAND_NAMES:
            df = pd.read_excel(self.path, engine="openpyxl", sheet_name=OLI_BAND_NAMES[self.band])
            wvl = np.array(df["Wavelength"])
            resp = np.array(df["BA RSR [watts]"])
        else:
            if self.platform_name == "Landsat-8":
                sheet_name = TIRS_SHEETNAMES_L8[self.band]
                band_name = TIRS_BAND_NAMES_L8[self.band]
            elif self.platform_name == "Landsat-9":
                sheet_name = TIRS_SHEETNAMES_L9[self.band]
                band_name = TIRS_BAND_NAMES_L9[self.band]
            df = pd.read_excel(self.path, engine="openpyxl", sheet_name=sheet_name)

            wvl = np.array(df["wavelength [um]"])
            resp = np.array(df[band_name])

        # Cut unneeded points
        pts = np.argwhere(resp > 0.002)
        wvl = np.squeeze(wvl[pts])
        resp = np.squeeze(resp[pts])

        self.rsr = {"wavelength": wvl,
                    "response": resp}


if __name__ == "__main__":
    bands = sorted(OLI_BAND_NAMES.keys()) + sorted(TIRS_BAND_NAMES_L8.keys())
    for platform_name in ["Landsat-8", "Landsat-9"]:
        tohdf5(OliRSR, platform_name, bands)
