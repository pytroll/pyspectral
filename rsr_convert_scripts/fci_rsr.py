#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Pytroll Community

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

"""Read the MTG FCI relative spectral response functions.

Data from EUMETSAT NWP-SAF:
https://nwpsaf.eu/downloads/rtcoef_rttov12/ir_srf/rtcoef_mtg_1_fci_srf.html
"""

import os
import logging
import numpy as np
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR

LOG = logging.getLogger(__name__)

FCI_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10',
                  'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16']


class FciRSR(InstrumentRSR):
    """Container for the MTG FCI RSR data."""

    def __init__(self, bandname, platform_name):
        """Setup the MTG FCI RSR data container."""
        super(FciRSR, self).__init__(bandname, platform_name, FCI_BAND_NAMES)

        self.instrument = 'fci'

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

    def _load(self, scale=10000.0):
        """Load the FCI RSR data for the band requested."""
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavenumber',
                                    'response'],
                             skip_header=4)

        # Data are wavenumbers in cm-1:
        wavelength = 1. / data['wavenumber'] * scale
        response = data['response']

        self.rsr = {'wavelength': wavelength[::-1], 'response': response[::-1]}


def main():
    """Main function creating the internal Pyspectral hdf5 output for FCI."""
    for platform_name in ["Meteosat-12", 'MTG-I1']:
        tohdf5(FciRSR, platform_name, FCI_BAND_NAMES)


if __name__ == "__main__":
    main()
