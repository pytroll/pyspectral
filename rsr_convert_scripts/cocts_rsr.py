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

"""Read the HY-1C COCTS relative spectral responses. Data from 
lwk1542@hotmail.com

NB! The two IR bands are NOT included.

See issue 
https://github.com/pytroll/pyspectral/issues/61
"""
import os
import numpy as np
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR

import logging
LOG = logging.getLogger(__name__)

COCTS_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8']


class COCTS_RSR(InstrumentRSR):

    """Container for the HY-1C COCTS RSR data"""

    def __init__(self, bandname, platform_name):

        super(COCTS_RSR, self).__init__(bandname, platform_name, COCTS_BAND_NAMES)

        self.instrument = INSTRUMENTS.get(platform_name, 'cocts')

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load(bandname)

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

    def _load(self, bandname, scale=0.001):
        """Load the COCTS RSR data for the band requested.
           Wavelength is given in nanometers.
        """
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavelength', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8'],
                             skip_header=0)

        wavelength = data['wavelength'] * scale
        response = data[bandname]

        self.rsr = {'wavelength': wavelength, 'response': response}


def main():
    """Main"""
    for platform_name in ["HY-1C", ]:
        tohdf5(COCTS_RSR, platform_name, COCTS_BAND_NAMES)


if __name__ == "__main__":
    main()
