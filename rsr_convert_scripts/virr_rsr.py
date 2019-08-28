#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Adam.Dybbroe
#
# Author(s):
#
#   David Hoese <david.hoese@ssec.wisc.edu>
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
"""Read the VIRR relative spectral responses.

Data from http://gsics.nsmc.org.cn/portal/en/fycv/srf.html

"""

import os
import numpy as np
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR

import logging
LOG = logging.getLogger(__name__)

VIRR_BAND_NAMES = {
    'FY-3B': ['ch{:d}'.format(x) for x in range(1, 11)],
    'FY-3C': ['ch1', 'ch2'] + ['ch{:d}'.format(x) for x in range(6, 11)],
}


class VirrRSR(InstrumentRSR):
    """Container for the FY-3B/FY-3C VIRR RSR data."""

    def __init__(self, bandname, platform_name):
        """Verify that file exists and can be read."""
        super(VirrRSR, self).__init__(bandname, platform_name, VIRR_BAND_NAMES[platform_name])

        self.instrument = INSTRUMENTS.get(platform_name, 'virr')
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
        """Load the VIRR RSR data for the band requested.

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
    for platform_name, band_names in VIRR_BAND_NAMES.items():
        tohdf5(VirrRSR, platform_name, band_names)


if __name__ == "__main__":
    main()
