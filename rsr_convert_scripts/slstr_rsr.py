#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, 2018 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

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
Sentinel-3 SLSTR spectral response function interface

https://sentinel.esa.int/documents/247904/322305/SLSTR_FM02_Spectral_Responses_Necdf_zip/3a4482b8-6e44-47f3-a8f2-79c000663976

"""

import os
from netCDF4 import Dataset
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR
import logging

LOG = logging.getLogger(__name__)

SLSTR_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4',
                    'ch5', 'ch6', 'ch7', 'ch8', 'ch9']


class SlstrRSR(InstrumentRSR):

    """Class for Sentinel-3 SLSTR RSR"""

    def __init__(self, bandname, platform_name):
        """
        Read the SLSTR relative spectral responses for all channels.

        """
        super(SlstrRSR, self).__init__(bandname, platform_name,
                                       SLSTR_BAND_NAMES)

        self.instrument = 'slstr'

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

        self.filename = self.requested_band_filename

    def _load(self, scale=1.0):
        """Load the SLSTR relative spectral responses
        """

        LOG.debug("File: %s", str(self.requested_band_filename))
        ncf = Dataset(self.requested_band_filename, 'r')

        wvl = ncf.variables['wavelength'][:] * scale
        resp = ncf.variables['response'][:]

        self.rsr = {'wavelength': wvl, 'response': resp}


def main():
    """Main"""
    for platform_name in ['Sentinel-3A', ]:
        tohdf5(SlstrRSR, platform_name, SLSTR_BAND_NAMES)


if __name__ == "__main__":
    main()
