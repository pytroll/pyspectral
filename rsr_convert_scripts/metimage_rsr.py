#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Adam.Dybbroe

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

"""Read the preliminary MetImage relative spectral response functions.
Data from the NWPSAF, These are very early theoretical and idealized versions,
derived from specifications I assume.

"""

import os
import numpy as np
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR
import logging

LOG = logging.getLogger(__name__)

METIMAGE_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5',
                       'ch6', 'ch7', 'ch8', 'ch9', 'ch10',
                       'ch11', 'ch12', 'ch13', 'ch14', 'ch15',
                       'ch16', 'ch17', 'ch18', 'ch19', 'ch20']


class MetImageRSR(InstrumentRSR):

    """Container for the EPS-SG MetImage RSR data"""

    def __init__(self, bandname, platform_name):

        super(MetImageRSR, self).__init__(
            bandname, platform_name, METIMAGE_BAND_NAMES)

        self.instrument = 'metimage'
        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

        self.unit = 'micrometer'
        self.wavespace = 'wavelength'

    def _load(self, scale=1.0):
        """Load the MetImage RSR data for the band requested"""
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavenumber',
                                    'response'],
                             skip_header=4)

        # Data are wavenumbers in cm-1:
        wavelength = 1. / data['wavenumber'] * 10000.
        response = data['response']

        self.rsr = {'wavelength': wavelength, 'response': response}


def main():
    """Main"""
    for platform_name in ["Metop-SG-A1", ]:
        tohdf5(MetImageRSR, platform_name, METIMAGE_BAND_NAMES)


if __name__ == "__main__":
    main()
