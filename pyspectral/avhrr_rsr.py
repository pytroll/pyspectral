#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015, 2016, 2017 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>
#   Panu Lahtinen <panu.lahtinen@fmi.fi>

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

"""Read the NOAA/Metop AVHRR relative spectral response functions.
Data from NOAA STAR.
https://www.star.nesdis.noaa.gov/smcd/spb/fwu/homepage/AVHRR/spec_resp_func/index.html
"""

import os
import numpy as np
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5

import logging
LOG = logging.getLogger(__name__)

AVHRR_BAND_NAMES = {'avhrr/3': ['ch1', 'ch2', 'ch3a', 'ch3b', 'ch4', 'ch5'],
                    'avhrr/2': ['ch1', 'ch2', 'ch3', 'ch4', 'ch5'],
                    'avhrr/1': ['ch1', 'ch2', 'ch3', 'ch4']}


from pyspectral.raw_reader import InstrumentRSR


class AvhrrRSR(InstrumentRSR):

    """Container for the NOAA/Metop AVHRR RSR data"""

    def __init__(self, bandname, platform_name):

        super(AvhrrRSR, self).__init__(
            bandname, platform_name,
            AVHRR_BAND_NAMES[INSTRUMENTS[platform_name]])

        self.instrument = INSTRUMENTS.get(platform_name, 'avhrr/3')

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            if self.instrument == 'avhrr/1':
                self._load(scale=0.001)
            else:
                self._load()

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

    def _load(self, scale=1.0):
        """Load the AVHRR RSR data for the band requested"""
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavelength',
                                    'response'],
                             skip_header=1)

        wavelength = data['wavelength'] * scale
        response = data['response']

        self.rsr = {'wavelength': wavelength, 'response': response}


def main():
    """Main"""
    for platform_name in ["NOAA-17", "NOAA-16", "NOAA-14", "NOAA-12",
                          "NOAA-11", "NOAA-9", "NOAA-7",
                          "NOAA-10", "NOAA-8", "NOAA-6", "TIROS-N",
                          "NOAA-15"]:
        tohdf5(AvhrrRSR, platform_name, AVHRR_BAND_NAMES[
               INSTRUMENTS[platform_name]])

if __name__ == "__main__":
    main()
