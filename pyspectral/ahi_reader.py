#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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

"""Read the Himawari AHI spectral response functions. Data from
http://cimss.ssec.wisc.edu/goes/calibration/SRF/ahi/ 
"""

import logging
LOG = logging.getLogger(__name__)

import os
import numpy as np

from pyspectral.utils import get_central_wave
from pyspectral import get_config


AHI_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5',
                  'ch6', 'ch7', 'ch8', 'ch9', 'ch10',
                  'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16']

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class AhiRSR(object):

    """Container for the Himawari AHI relative spectral response data"""

    def __init__(self, bandname, satname='himawari8'):
        """
        """
        self.satname = satname
        self.bandname = bandname
        self.filenames = {}
        self.rsr = None

        conf = get_config()
        options = {}
        for option, value in conf.items(self.satname + '-ahi', raw=True):
            options[option] = value

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')

        self._get_bandfilenames(**options)
        LOG.debug("Filenames: " + str(self.filenames))
        if os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

    def _get_bandfilenames(self, **options):
        """Get the AHI rsr filenames"""

        path = options["path"]
        for band in AHI_BAND_NAMES:
            LOG.debug("Band = " + str(band))
            self.filenames[band] = os.path.join(path, options[band])
            LOG.debug(self.filenames[band])
            if not os.path.exists(self.filenames[band]):
                LOG.warning("Couldn't find an existing file for this band: " +
                            str(self.filenames[band]))

    def _load(self):
        """Load the Himawari AHI RSR data for the band requested
        """

        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavenumber',
                                    'response'])
        # Data seems to be wavenumbers (in some unit...)
        # Now, provide wavelengths in micro meters
        wavelength = 1.e4 / data['wavenumber']
        response = data['response']

        idx = np.argsort(wavelength)
        wavelength = np.take(wavelength, idx)
        response = np.take(response, idx)
        self.rsr = {}
        self.rsr['det-1'] = {'wavelength': wavelength,
                             'response': response}


def convert2hdf5(platform_id, sat_number):
    """Retrieve original RSR data and convert to internal hdf5 format"""

    import h5py

    satellite_id = platform_id + str(sat_number)

    ahi = AhiRSR('ch1', satellite_id)
    filename = os.path.join(ahi.output_dir,
                            "rsr_ahi_%s%d.h5" % (platform_id, sat_number))

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for AHI'
        h5f.attrs['platform'] = platform_id
        h5f.attrs['sat_number'] = sat_number
        h5f.attrs['band_names'] = AHI_BAND_NAMES

        for chname in AHI_BAND_NAMES:
            ahi = AhiRSR(chname, satellite_id)
            grp = h5f.create_group(chname)
            wvl = ahi.rsr[
                'det-1']['wavelength'][~np.isnan(ahi.rsr['det-1']['wavelength'])]
            rsp = ahi.rsr[
                'det-1']['response'][~np.isnan(ahi.rsr['det-1']['wavelength'])]
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = ahi.rsr['det-1']['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = 1e-06
            dset[...] = arr
            arr = ahi.rsr['det-1']['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr


if __name__ == "__main__":

    import sys
    LOG = logging.getLogger('ahi_rsr')
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    #ahi = AhiRSR('ch1', 'himawari8')
    convert2hdf5('himawari', 8)
