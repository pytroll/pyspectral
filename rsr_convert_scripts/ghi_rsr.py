#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2023 Pytroll developers
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

"""Read the FY-4B GHI relative spectral responses.

Data from https://img.nsmc.org.cn/PORTAL/NSMC/DATASERVICE/SRF/FY4B/FY4B_GHI_SRF.zip
"""
import os

import numpy as np

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.utils import get_logger, logging_on

FY4_GHI_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7']
BANDNAME_SCALE2MICROMETERS = {'FY-4B': {'ch1': 0.001,
                                        'ch2': 0.001,
                                        'ch3': 0.001,
                                        'ch4': 0.001,
                                        'ch5': 0.001,
                                        'ch6': 0.001,
                                        'ch7': 1.0,
                                        }}


class GHIRSR(InstrumentRSR):
    """Container for the FY-4 GHI RSR data."""

    def __init__(self, bandname, platform_name):
        """Initialise the FY-4 GHI relative spectral response data."""
        super(GHIRSR, self).__init__(bandname, platform_name, FY4_GHI_BAND_NAMES)

        self.instrument = INSTRUMENTS.get(platform_name, 'ghi')
        if type(self.instrument) is list:
            self.instrument = 'ghi'

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            scale = BANDNAME_SCALE2MICROMETERS[platform_name].get(bandname)
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
        """Load the GHI RSR data for the band requested.

        Wavelength is given in nanometers.
        """
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True, delimiter='\t',
                             names=['wavelength',
                                    'response'],
                             skip_header=1)

        wavelength = data[0] * scale
        response = data[1]

        # Response can be either 0-1 or 0-100 depending on RSR source - this scales to 0-1 range.
        if np.nanmax(response > 1):
            response = response / 100.

        # Cut unneeded points
        pts = np.argwhere(response > 0.001)

        wavelength = np.squeeze(wavelength[pts])
        response = np.squeeze(response[pts])

        self.rsr = {'wavelength': wavelength, 'response': response}


def convert_ghi():
    """Read original GHI RSR data and convert to common Pyspectral hdf5 format."""
    # For FY-4B
    tohdf5(GHIRSR, 'FY-4B', FY4_GHI_BAND_NAMES)


if __name__ == "__main__":
    LOG = get_logger(__name__)
    logging_on()

    convert_ghi()
