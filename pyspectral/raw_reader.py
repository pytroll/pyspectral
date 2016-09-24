#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

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

"""Base class for reading raw instrument spectral responses 
"""

import ConfigParser
import os
import numpy as np

import logging
LOG = logging.getLogger(__name__)

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")


class InstrumentRSR(object):

    """Base class for the raw (agency dependent) instrument response functions"""

    def __init__(self, bandname, platform_name, bandnames=None):
        self.platform_name = platform_name
        self.bandname = bandname
        self.instrument = None
        self.filenames = {}
        self.requested_band_filename = None
        self.bandnames = bandnames
        if not self.bandnames:
            self.bandnames = []
        for band in self.bandnames:
            self.filenames[band] = None
        self.rsr = None

        self.output_dir = None
        self.path = None
        self.options = {}
        self.requested_band_filename = None

    def _get_options_from_config(self):

        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception('Failed reading configuration file: %s',
                          str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items(self.platform_name + '-' +
                                        self.instrument,
                                        raw=True):
            options[option] = value

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')
        self.path = options['path']
        self.options = options

    def _get_bandfilenames(self):
        """Get the instrument rsr filenames"""
        for band in self.bandnames:
            LOG.debug("Band = %s", str(band))
            self.filenames[band] = os.path.join(self.path, self.options[band])
            LOG.debug(self.filenames[band])
            if not os.path.exists(self.filenames[band]):
                LOG.warning("Couldn't find an existing file for this band: %s",
                            str(self.filenames[band]))

    def _load(self, scale=1.0):
        """Load the instrument RSR from file(s)"""

        raise NotImplementedError(
            "Instrument rsr loader needs to be defined in the subclass")
