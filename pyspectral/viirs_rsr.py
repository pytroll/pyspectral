#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014 Adam.Dybbroe

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

"""Interface to VIIRS relative spectral responses
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

import numpy as np

class ViirsRSR(object):
    """Container for the (S-NPP) VIIRS RSR data"""
    def __init__(self, bandname, satname='npp'):
        """
        """
        self.satname = satname
        self.bandname = bandname
        self.filename = None
        self.rsr = None

        self._get_bandfile()
        LOG.debug("Filename: " + str(self.filename))
        self._load()

    def _get_bandfile(self):
        """Get the VIIRS rsr filename"""

        band_file = None
        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception('Failed reading configuration file: ' + str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items('viirs', raw = True):
            options[option] = value

        values = {"bandname": self.bandname}

        paths = [options["iband_visnir_path"],
                 options["iband_ir_path"],
                 options["mband_visnir_path"],
                 options["mband_ir_path"]
                 ]
        fnames = [options["iband_visnir_names"] % values,
                  options["iband_ir_names"] % values,
                  options["mband_visnir_names"] % values,
                  options["mband_ir_names"] % values
                  ]
                  
        for path, fname in zip(paths, fnames):
            band_file = os.path.join(path, fname)
            if os.path.exists(band_file):
                self.filename = band_file
                return

        if not band_file:
            raise IOError("Couldn't find an existing file for this band: " + 
                          str(self.bandname))


    def _load(self, scale=0.001):
        """Load the VIIRS RSR data for the band requested
        """
        import numpy as np
        
        try:
            data = np.genfromtxt(self.filename, 
                                 unpack=True, 
                                 names=['bandname', 
                                        'detector',
                                        'subsample',
                                        'wavelength',
                                        'band_avg_snr',
                                        'asr',
                                        'response',
                                        'quality_flag',
                                        'xtalk_flag'])
        except ValueError:
            data = np.genfromtxt(self.filename, 
                                 unpack=True, 
                                 names=['bandname', 
                                        'detector',
                                        'subsample',
                                        'wavelength',
                                        'response'])
            
        wavelength = data['wavelength'] * scale
        response = data['response']
        det = data['detector']
        
        detectors = {}
        for idx in range(int(max(det))):
            detectors["det-%d" % (idx+1)] = {}
            detectors["det-%d" % (idx+1)]['wavelength'] = np.repeat(wavelength, np.equal(det,idx+1))
            detectors["det-%d" % (idx+1)]['response'] = np.repeat(response, np.equal(det,idx+1))

        self.rsr = detectors
        
