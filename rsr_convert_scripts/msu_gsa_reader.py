#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Pytroll developers
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

"""Read the Arctica-M N1 MSU-GS/A spectral response functions.

Data from Roshydromet via personal communication.
"""

import logging

import pandas as pd

from pyspectral.config import get_config
from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

# Names of the individual bands
MSUGSA_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5',
                     'ch6', 'ch7', 'ch8', 'ch9', 'ch10']

# Set up VIS and IR bands, needed for selecting sheet in RSR file
VISBANDS = {'ch1', 'ch2', 'ch3'}
IRBANDS = {'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10'}

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class MsugsaRSR(InstrumentRSR):
    """Container for the Arctica-M-N1 MSU-GS/A relative spectral response data."""

    def __init__(self, bandname, platform_name):
        """Initialize the MSU-GS/A RSR class."""
        super(MsugsaRSR, self).__init__(
            bandname, platform_name, MSUGSA_BAND_NAMES)

        self.instrument = 'msu-gsa'
        self.platform_name = platform_name

        options = get_config()

        self.msugsa_path = options[
            self.platform_name + '-' + self.instrument].get('path')

        self.output_dir = options.get('rsr_dir', './')

        self._load()

    def _load(self, scale=10000.0):
        """Load the MSU-GS/A RSR data for the band requested."""
        detectors = {}
        # The Arctica satellites have two instruments on them. Pyspectral isn't set up
        # to handle this, so instead we call them separate detectors.
        for detnum in (1, 2):
            if self.bandname in VISBANDS:
                data = pd.read_excel(self.msugsa_path, sheet_name=f'MSU-{detnum} vis', skiprows=2,
                                     names=['wvl', 'ch1', 'ch2', 'ch3'])
            elif self.bandname in IRBANDS:
                data = pd.read_excel(self.msugsa_path, sheet_name=f'MSU-{detnum} IR', skiprows=2,
                                     names=['wvl', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10'])
            else:
                raise KeyError(f"{self.bandname} is not a valid VIS or IR band!")
            wavelength = data['wvl']
            response = data[self.bandname]

            detectors[f'det-{detnum}'] = {'wavelength': wavelength, 'response': response}

        self.rsr = detectors


if __name__ == "__main__":
    import sys
    LOG = logging.getLogger('msu_gsa_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    for platform_name in ['Arctica-M-N1', ]:
        tohdf5(MsugsaRSR, platform_name, MSUGSA_BAND_NAMES, detectors=['det-1', 'det-2'])
