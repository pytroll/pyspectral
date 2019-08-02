#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, 2019 Pytroll

# Author(s):

#   Xin.Zhang <xinzhang1215@gmail.com>
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

"""Read the FY-4A AGRI relative spectral responses. Data from
http://fy4.nsmc.org.cn/portal/cn/fycv/srf.html
"""
import os
import numpy as np
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import logging_on, get_logger

FY4A_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8',
                   'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14']
BANDNAME_SCALE2MICROMETERS = {'ch1': 0.001,
                              'ch2': 0.001,
                              'ch3': 0.001,
                              'ch4': 1.0,
                              'ch5': 1.0,
                              'ch6': 1.0,
                              'ch7': 1.0,
                              'ch8': 1.0,
                              'ch9': 1.0,
                              'ch10': 1.0,
                              'ch11': 1.0,
                              'ch12': 1.0,
                              'ch13': 1.0,
                              'ch14': 1.0}


class AGRIRSR(InstrumentRSR):
    """Container for the FY-4 AGRI RSR data"""

    def __init__(self, bandname, platform_name):
        """Initialise the FY-4 AGRI relative spectral response data"""
        super(AGRIRSR, self).__init__(bandname, platform_name, FY4A_BAND_NAMES)

        self.instrument = INSTRUMENTS.get(platform_name, 'agri')

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            scale = BANDNAME_SCALE2MICROMETERS.get(bandname)
            if scale:
                self._load(scale=scale)
            else:
                LOG.error(
                    "Failed determine the scale used to convert to wavelength in micrometers - channel = %s", bandname)
                raise AttributeError('no scale for bandname %s', bandname)

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        self.filename = self.requested_band_filename

    def _load(self, scale=0.001):
        """Load the AGRI RSR data for the band requested

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
    for platform_name in ["FY-4A", ]:
        tohdf5(AGRIRSR, platform_name, FY4A_BAND_NAMES)


if __name__ == "__main__":
    LOG = get_logger(__name__)
    logging_on()

    main()
