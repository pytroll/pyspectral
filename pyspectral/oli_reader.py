#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, 2018 Adam.Dybbroe

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

"""Landsat-8 OLI reader
"""

import os
from xlrd import open_workbook
import numpy as np
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR
import logging
LOG = logging.getLogger(__name__)


OLI_BAND_NAMES = {'CoastalAerosol': 'B1',
                  'Blue': 'B2',
                  'Green': 'B3',
                  'Red': 'B4',
                  'NIR': 'B5',
                  'Cirrus': 'B9',
                  'SWIR1': 'B6',
                  'SWIR2': 'B7',
                  'Pan': 'B8'}


class OliRSR(InstrumentRSR):

    """Class for Landsat OLI RSR"""

    def __init__(self, bandname, platform_name):
        """
        Read the Landsat OLI relative spectral responses for all channels.

        """
        super(OliRSR, self).__init__(bandname, platform_name)

        self.instrument = 'oli'
        self._get_options_from_config()

        LOG.debug("Filename: %s", str(self.path))
        if os.path.exists(self.path):
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, scale=0.001):
        """Load the Landsat OLI relative spectral responses
        """

        with open_workbook(self.path) as wb_:
            for sheet in wb_.sheets():
                if sheet.name in ['Plot of AllBands', ]:
                    continue
                ch_name = OLI_BAND_NAMES.get(sheet.name.strip())

                if ch_name != self.bandname:
                    continue

                wvl = sheet.col_values(0, 2)
                resp = sheet.col_values(1, 2)

                self.rsr = {'wavelength': np.array(wvl) / 1000.,
                            'response': np.array(resp)}
                break


def main():
    """Main"""
    bands = OLI_BAND_NAMES.values()
    bands.sort()
    for platform_name in ['Landsat-8', ]:
        tohdf5(OliRSR, platform_name, bands)


if __name__ == "__main__":
    main()
