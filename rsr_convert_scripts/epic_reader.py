#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Pytroll developers
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

"""Read the DSCOVR-EPIC spectral response functions.

Data from the NASA Goddard website:
https://avdc.gsfc.nasa.gov/pub/DSCOVR/EPIC_Filter_Data/

"""

import logging
import os

import numpy as np
import pandas as pd

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)


EPIC_BAND_NAMES = {'B317': 'T(317.5) %',
                   'B325': 'T(325) %',
                   'B340': 'T(340) %',
                   'B388': 'T(388) %',
                   'B443': 'T(443) %',
                   'B551': 'T(551) %',
                   'B680': 'T(680) %',
                   'B688': 'T(687.75) %',
                   'B764': 'T(764) %',
                   'B780': 'T(779.5) %'}

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class EpicRSR(InstrumentRSR):
    """Container for the DSCOVR EPIC relative spectral response data."""

    def __init__(self, bandname, platform_name):
        """Initialize the EPIC RSR class."""
        super(EpicRSR, self).__init__(
            bandname, platform_name, EPIC_BAND_NAMES.keys())

        self.instrument = 'epic'
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
        """Load the EPIC relative spectral responses."""
        df1 = pd.read_excel(self.path,
                            sheet_name='Data',
                            skiprows=4,
                            engine='openpyxl')
        # Remove empty row from the data
        df1.drop(df1.index[0], inplace=True)
        # Column names don't match band names - so we use a dict to find correct
        # columns. We also need to find the column with the wavelength data.
        # This is the column before the actual RSR data for each band.
        col_pos = df1.columns.get_loc(EPIC_BAND_NAMES[self.bandname])
        wvl_data = df1.iloc[:, col_pos - 1]
        srf_data = df1.iloc[:, col_pos]

        # Not all bands have an identical number of RSR points, so we need to
        # remove NaNs from the data.
        wvl_data.dropna(inplace=True)
        srf_data.dropna(inplace=True)

        # Data is in nanometers, so we need to convert to micrometers.
        self.rsr = {'wavelength': np.array(wvl_data) / 1000,
                    'response': np.array(srf_data) / np.nanmax(srf_data)}


if __name__ == "__main__":
    import sys
    LOG = logging.getLogger('epic_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    for platform_name in ['DSCOVR', ]:
        tohdf5(EpicRSR, platform_name, list(EPIC_BAND_NAMES.keys()))
