#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015, 2016 Adam.Dybbroe

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
"""


import os
import numpy as np

from pyspectral.utils import get_central_wave
from pyspectral.utils import INSTRUMENTS

import logging
LOG = logging.getLogger(__name__)
from pyspectral import get_config


AVHRR_BAND_NAMES = ['ch1', 'ch2', 'ch3a', 'ch3b', 'ch4', 'ch5']


class AvhrrRSR(object):

    """Container for the NOAA/Metop AVHRR RSR data"""

    def __init__(self, bandname, satname):
        self.satname = satname
        self.bandname = bandname
        self.instrument = INSTRUMENTS.get(satname, 'avhrr')
        self.filenames = {}
        self.requested_band_filename = None
        for band in AVHRR_BAND_NAMES:
            self.filenames[band] = None
        self.rsr = None

        conf = get_config()
        options = {}
        for option, value in conf.items(self.satname + '-' +
                                        self.instrument,
                                        raw=True):
            options[option] = value

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')

        self._get_bandfilenames(**options)
        LOG.debug("Filenames: %s", str(self.filenames))
        if os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

    def _get_bandfilenames(self, **options):
        """Get the AVHRR rsr filenames"""
        path = options["path"]
        for band in AVHRR_BAND_NAMES:
            LOG.debug("Band = %s", str(band))
            self.filenames[band] = os.path.join(path, options[band])
            LOG.debug(self.filenames[band])
            if not os.path.exists(self.filenames[band]):
                LOG.warning("Couldn't find an existing file for this band: %s",
                            str(self.filenames[band]))

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


def convert2hdf5(platform_name):
    """Retrieve original RSR data and convert to internal hdf5 format"""
    import h5py

    avhrr = AvhrrRSR('ch1', platform_name)
    filename = os.path.join(avhrr.output_dir,
                            "rsr_%s_%s.h5" % (avhrr.instrument.replace('/', ''),
                                              platform_name))

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for AVHRR'
        h5f.attrs['platform_name'] = platform_name
        h5f.attrs['band_names'] = AVHRR_BAND_NAMES

        for chname in AVHRR_BAND_NAMES:
            avhrr = AvhrrRSR(chname, platform_name)
            grp = h5f.create_group(chname)
            wvl = avhrr.rsr['wavelength'][~np.isnan(avhrr.rsr['wavelength'])]
            rsp = avhrr.rsr['response'][~np.isnan(avhrr.rsr['wavelength'])]
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = avhrr.rsr['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = 1e-06
            dset[...] = arr
            arr = avhrr.rsr['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr


def main():
    """Main"""
    for platform_name in ["NOAA-18", "NOAA-19"]:
        convert2hdf5(platform_name)

if __name__ == "__main__":
    main()
