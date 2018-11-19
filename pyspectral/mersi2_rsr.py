#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Adam.Dybbroe

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

"""Read the MERSI-II relative spectral responses. Data from xuna@cma.gov.cn
(Personal contact with Sara Hörnquist, SMHI).
"""
import os
import numpy as np
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR

import logging
LOG = logging.getLogger(__name__)

MERSI2_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8',
                     'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16',
                     'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24',
                     'ch25']


class Mersi2RSR(InstrumentRSR):

    """Container for the FY3D MERSI-II RSR data"""

    def __init__(self, bandname, platform_name):

        super(Mersi2RSR, self).__init__(bandname, platform_name, MERSI2_BAND_NAMES)

        self.instrument = INSTRUMENTS.get(platform_name, 'mersi-2')

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

    def _load(self, scale=0.001):
        """Load the MERSI-2 RSR data for the band requested.
           Wavelength is given in nanometers.
        """
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavelength',
                                    'response'],
                             skip_header=0)

        wavelength = data['wavelength'] * scale
        response = data['response']

        self.rsr = {'wavelength': wavelength, 'response': response}


def main():
    """Main"""
    for platform_name in ["FY-3D", ]:
        tohdf5(Mersi2RSR, platform_name, MERSI2_BAND_NAMES)


if __name__ == "__main__":
    main()
