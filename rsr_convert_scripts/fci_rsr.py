#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020-2022 Pytroll developers
#
# Author(s):
#
#   Adam.Dybbroe <adam.dybbroe@smhi.se>
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

"""Read the MTG FCI relative spectral response functions.

Data from EUMETSAT:
https://sftp.eumetsat.int/public/folder/UsCVknVOOkSyCdgpMimJNQ/User-Materials/MTGUP/Materials/FCI-SRF_Apr2022/
"""

import logging
from netCDF4 import Dataset
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR

LOG = logging.getLogger(__name__)

FCI_BAND_NAMES = ['VIS0.4', 'VIS0.5', 'VIS0.6_HR', 'VIS0.8', 'VIS0.9', 'NIR1.3',
                  'NIR1.6', 'NIR2.2_HR', 'IR3.8_HR', 'WV6.3', 'WV7.3', 'IR8.7',
                  'IR9.7', 'IR10.5_HR', 'IR12.3', 'IR13.3']


class FciRSR(InstrumentRSR):
    """Container for the MTG FCI RSR data."""

    def __init__(self, bandname, platform_name):
        """MTG FCI RSR data container."""
        super().__init__(bandname, platform_name)

        self.instrument = 'fci'
        self._get_options_from_config()

        LOG.debug("Filename with all bands: %s", str(self.filename))
        self._load()

    def _load(self, scale=1000000.0):
        """Load the FCI RSR data for the band requested."""
        LOG.debug("File: %s", str(self.filename))

        ncf = Dataset(self.path / self.filename, 'r')

        wvl = ncf.variables['wavelength'][:] * scale
        resp = ncf.variables['srf'][:]

        bandnames = ncf.variables['channel_id'][:]
        for idx, band_name in enumerate(bandnames):
            if band_name == self.bandname:
                self.rsr = {'wavelength': wvl[:, idx], 'response': resp[:, idx]}


def main():
    """Ccreate the internal Pyspectral hdf5 output for FCI."""
    for platform_name in ["Meteosat-12", 'MTG-I1']:
        tohdf5(FciRSR, platform_name, FCI_BAND_NAMES)


if __name__ == "__main__":
    main()
