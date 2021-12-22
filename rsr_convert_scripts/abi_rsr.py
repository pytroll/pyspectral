#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 - 2021 Pytroll developers
#
# Author(s):
#
#   Adam Dybbroe <Firstname.Lastname@smhi.se>
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

"""Read raw GOES-R series ABI RSR and generate HDF5 files.

Reading the original raw GOES-R ABI spectral responses and generating the
internal pyspectral formatet hdf5.

https://ncc.nesdis.noaa.gov/GOESR/ABI.php

"""

import os
import numpy as np
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR
import logging

LOG = logging.getLogger(__name__)

ABI_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4',
                  'ch5', 'ch6', 'ch7', 'ch8',
                  'ch9', 'ch10', 'ch11', 'ch12',
                  'ch13', 'ch14', 'ch15', 'ch16']


class AbiRSR(InstrumentRSR):
    """Class for GOES-R ABI RSR."""

    def __init__(self, bandname, platform_name):
        """Read the GOES-R ABI relative spectral responses for all channels."""
        super(AbiRSR, self).__init__(bandname, platform_name,
                                     ABI_BAND_NAMES)

        self.instrument = 'abi'

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
        """Load the ABI relative spectral responses."""
        LOG.debug("File: %s", str(self.requested_band_filename))

        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             skip_header=2)
        wvl = data[0] * scale
        resp = data[2]

        self.rsr = {'wavelength': wvl, 'response': resp}


def main():
    """Create pyspectral hdf5 RSR files for all GOES sats."""
    for platform_name in ['GOES-16', 'GOES-17', 'GOES-18', 'GOES-19']:
        tohdf5(AbiRSR, platform_name, ABI_BAND_NAMES)


if __name__ == "__main__":
    main()
