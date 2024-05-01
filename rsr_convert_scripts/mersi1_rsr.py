#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2024 Pytroll developers
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

"""Read the MERSI-1 relative spectral responses.

Data available from NSMC:
https://img.nsmc.org.cn/PORTAL/NSMC/DATASERVICE/SRF/FY3A/FY3A_MERSI_SRF.rar
https://img.nsmc.org.cn/PORTAL/NSMC/DATASERVICE/SRF/FY3B/FY3B_MERSI_SRF.rar
https://img.nsmc.org.cn/PORTAL/NSMC/DATASERVICE/SRF/FY3C/FY3C_MERSI_SRF.rar

"""
import logging
import os

import numpy as np

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

MERSI1_FY3AC_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8',
                           'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16',
                           'ch17', 'ch18', 'ch19', 'ch20']
MERSI1_FY3B_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch6', 'ch7', 'ch8',
                          'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16',
                          'ch17', 'ch18', 'ch19', 'ch20']


class Mersi1FY3ABRSR(InstrumentRSR):
    """Container for the FY3A/B/C MERSI-1 RSR data."""

    def __init__(self, bandname, platform_name):
        """Initialize the MERSI-1 RSR class."""
        # FY-3B RSR doesn't have ch5(IR) band
        mersi1_band_names = MERSI1_FY3AC_BAND_NAMES if platform_name != "FY-3B" else MERSI1_FY3B_BAND_NAMES
        super(Mersi1FY3ABRSR, self).__init__(bandname, platform_name, mersi1_band_names)

        self.instrument = INSTRUMENTS.get(platform_name, 'mersi-1')
        if type(self.instrument) is list:
            self.instrument = 'mersi-1'

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        self.filename = self.requested_band_filename

    def _load(self, scale=0.001):
        """Load the MERSI-1 RSR data for the band requested.

        Wavelength is given in nanometers.
        """
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             skip_header=0)
        wavelength = data[0] * scale

        if self.platform_name != "FY-3B":
            response = data[1]
        else:
            # FY-3B RSRs are organized in two files
            fy3b_file1_bands_part1 = ["ch1", "ch2", "ch3", "ch4"]
            fy3b_file1_bands_part2 = ["ch8", "ch9", "ch10", "ch11", "ch12", "ch13", "ch14", "ch15", "ch16", "ch17",
                                      "ch18", "ch19", "ch20"]
            fy3b_file2_bands = ["ch6", "ch7"]
            if self.bandname in fy3b_file1_bands_part1:
                response = data[fy3b_file1_bands_part1.index(self.bandname) + 1]
            elif self.bandname in fy3b_file1_bands_part2:
                response = data[fy3b_file1_bands_part2.index(self.bandname) + 4]
            else:
                response = data[fy3b_file2_bands.index(self.bandname) + 1]

        # Cut unneeded points
        pts = np.argwhere(response > 0.001)
        wavelength = np.squeeze(wavelength[pts])
        response = np.squeeze(response[pts])

        # It is possible that some points of bands 1/2/3 where wavelength > 800 still has response > 0.001
        # They're out of the wavelength range of the band.
        # And will trigger a warning in pyspectral when doing atmospheric corrections
        # So let's cut these points
        if self.bandname in ["1", "2", "3"]:
            pts2 = np.argwhere(data['wavelength'] < 800)
            wavelength = np.squeeze(wavelength[pts2])
            response = np.squeeze(response[pts2])

        self.rsr = {'wavelength': wavelength, 'response': response}


if __name__ == "__main__":
    for platform_name in ["FY-3A", "FY-3B", "FY-3C"]:
        band_list = MERSI1_FY3AC_BAND_NAMES if platform_name != "FY-3B" else MERSI1_FY3B_BAND_NAMES
        tohdf5(Mersi1FY3ABRSR, platform_name, band_list)
