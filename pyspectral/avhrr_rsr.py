#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Adam.Dybbroe

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

"""Read the NOAA/Metop AVHRR relative spectral response functions. Data from
NOAA STAR.
"""

import logging
LOG = logging.getLogger(__name__)

import ConfigParser
import os

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " + 
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")

AVHRR_BAND_NAMES = ['ch1', 'ch2', 'ch3a', 'ch3b', 'ch4', 'ch5']


class AvhrrRSR(object):
    """Container for the NOAA/Metop AVHRR RSR data"""
    def __init__(self, bandname, satname):
        """
        """
        self.satname = satname
        self.bandname = bandname
        self.filenames = {}
        self.requested_band_filename = None
        for band in AVHRR_BAND_NAMES:
            self.filenames[band] = None
        self.rsr = None

        self._get_bandfilenames()
        LOG.debug("Filenames: " + str(self.filenames))
        if os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " + 
                          str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename 

    def _get_bandfilenames(self):
        """Get the AVHRR rsr filenames"""

        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception('Failed reading configuration file: ' + str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items(self.satname + '-avhrr', raw = True):
            options[option] = value

        path = options["path"]
        for band in AVHRR_BAND_NAMES:
            LOG.debug("Band= " + str(band))
            self.filenames[band] = os.path.join(path, options[band])
            LOG.debug(self.filenames[band])
            if not os.path.exists(self.filenames[band]):
                LOG.warning("Couldn't find an existing file for this band: " + 
                            str(self.filenames[band]))

    def _load(self, scale=1.0):
        """Load the AVHRR RSR data for the band requested
        """
        import numpy as np

        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True, 
                             names=['wavelength',
                                    'response'])

        wavelength = data['wavelength'] * scale
        response = data['response']

        self.rsr = {'wavelength': wavelength, 'response': response}
