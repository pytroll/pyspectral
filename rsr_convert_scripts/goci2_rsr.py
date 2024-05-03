#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Pytroll developers
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

"""Read the GeoKompsat-2B / GOCI-II spectral response functions.

Data from the Korea Ocean Satellite Centre website:
https://kosc.kiost.ac.kr/index.nm?menuCd=44&lang=en

The direct link to the SRFs is: https://kosc.kiost.ac.kr/upload/GOCI-II_SRF_Measured.csv

"""

import logging
import os

import numpy as np
import pandas as pd

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

GOCI2_BAND_NAMES = {"L380": "B1 (380 nm)",
                    "L412": "B2 (412 nm)",
                    "L443": "B3 (443 nm)",
                    "L490": "B4 (490 nm)",
                    "L510": "B5 (510 nm)",
                    "L555": "B6 (555 nm)",
                    "L620": "B7 (620 nm)",
                    "L660": "B8 (660 nm)",
                    "L680": "B9 (680 nm)",
                    "L709": "B10 (709 nm)",
                    "L745": "B11 (745 nm)",
                    "L865": "B12 (865 nm)"}

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class GOCI2RSR(InstrumentRSR):
    """Container for the GK-2B GOCI2 relative spectral response data."""

    def __init__(self, bandname, platform_name):
        """Initialize the GOCI2 RSR class."""
        super(GOCI2RSR, self).__init__(
            bandname, platform_name, GOCI2_BAND_NAMES.keys())

        self.instrument = 'goci2'
        self._get_options_from_config()

        LOG.debug("Filename: %s", str(self.path))
        if os.path.exists(self.path):
            self._load()
        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

        self.unit = 'micrometer'
        self.wavespace = 'wavelength'

    def _load(self, scale=10000.0):
        """Load the GOCI2 relative spectral responses."""
        df1 = pd.read_csv(self.path)

        # Column names don't match band names - so we use a dict to find correct
        # columns. We also need to find the column with the wavelength data.
        # This is the column before the actual RSR data for each band.
        col_pos = df1.columns.get_loc(GOCI2_BAND_NAMES[self.bandname])
        wvl_data = df1.iloc[:, col_pos - 1]
        srf_data = df1.iloc[:, col_pos]

        # Not all bands have an identical number of RSR points, so we need to
        # remove NaNs from the data.
        wvl_data.dropna(inplace=True)
        srf_data.dropna(inplace=True)

        # Data is in nanometers, so we need to convert to micrometers.
        # The SRFs should already be normalised to 1, but we normalise here just to be sure.
        self.rsr = {'wavelength': np.array(wvl_data) / 1000,
                    'response': np.array(srf_data) / np.nanmax(srf_data)}


if __name__ == "__main__":
    import sys
    LOG = logging.getLogger('goci2_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    for platform_name in ['GK-2B', ]:
        tohdf5(GOCI2RSR, platform_name, list(GOCI2_BAND_NAMES.keys()))
