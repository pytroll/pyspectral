#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Simon R. Proud.
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

"""Sentinel-3 SLSTR spectral response function interface in TXT format.

This version of the SLSTR SRF reader works with the NWP SAF files in
plaintext format. It is required as the Sentiwiki page does not yet have
the SRFs for the -C and -D units of SLSTR.

See:
https://nwp-saf.eumetsat.int/site/software/rttov/download/coefficients/spectral-response-functions/

"""

import logging
import os

import numpy as np

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

SLSTR_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4',
                    'ch5', 'ch6', 'ch7', 'ch8', 'ch9']


class SlstrTxtRSR(InstrumentRSR):
    """Class for Sentinel-3 SLSTR RSR."""

    def __init__(self, bandname, platform_name):
        """Read the SLSTR relative spectral responses for all channels."""
        super(SlstrTxtRSR, self).__init__(bandname, platform_name,
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
        """Load the SLSTR relative spectral responses."""
        LOG.debug("File: %s", str(self.requested_band_filename))
        
        rsr_data = np.genfromtxt(self.requested_band_filename, skip_header=4)

        wvn = rsr_data[:, 0][::-1]
        resp = rsr_data[:, 1][::-1]

        # Spectral data is in wavenumber, convert to wavelength
        wvl = 10000. / wvn

        self.rsr = {'wavelength': wvl, 'response': resp}


if __name__ == "__main__":
    for platform_name in ['Sentinel-3A', 'Sentinel-3B', 'Sentinel-3C', 'Sentinel-3D', ]:
        tohdf5(SlstrTxtRSR, platform_name, SLSTR_BAND_NAMES)
