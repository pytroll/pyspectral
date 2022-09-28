#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Pytroll developers
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

"""Read the Electro-L N2 MSU-GS spectral response functions. Data from the NWPSAF:
https://nwp-saf.eumetsat.int/downloads/rtcoef_rttov13/ir_srf/rtcoef_electro-l_2_msugs_srf.html

"""

import os
import numpy as np
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.raw_reader import InstrumentRSR
import logging

LOG = logging.getLogger(__name__)

MSUGS_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5',
                    'ch6', 'ch7', 'ch8', 'ch9', 'ch10']

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class MsugsRSR(InstrumentRSR):
    """Container for the Electro-L N2 MSU-GS relative spectral response data"""

    def __init__(self, bandname, platform_name):

        super(MsugsRSR, self).__init__(
            bandname, platform_name, MSUGS_BAND_NAMES)

        self.instrument = 'msu-gs'
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

        self.unit = 'micrometer'
        self.wavespace = 'wavelength'

    def _load(self, scale=10000.0):
        """Load the MSU-GS RSR data for the band requested"""
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavenumber',
                                    'response'],
                             skip_header=4)

        # Data are wavenumbers in cm-1:
        wavelength = 1. / data[0][::-1] * scale
        response = data[1][::-1]

        # The real MSU-GS likely has multiple detectors. However, for now
        # we store the single rsr available in the NWPSAF coefficient files:
        self.rsr = {'wavelength': wavelength, 'response': response}


def main():
    """Main"""
    for platform_name in ['Electro-L-N2', ]:
        tohdf5(MsugsRSR, platform_name, MSUGS_BAND_NAMES)


if __name__ == "__main__":
    import sys

    LOG = logging.getLogger('msu_gs_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    main()
