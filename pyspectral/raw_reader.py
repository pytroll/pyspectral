#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2019 Adam.Dybbroe

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

"""Base class for reading raw instrument spectral responses."""

import os
import logging
from pyspectral.config import get_config

LOG = logging.getLogger(__name__)


class InstrumentRSR(object):
    """Base class for the raw (agency dependent) instrument response functions."""

    def __init__(self, bandname, platform_name, bandnames=None):
        """Initialize the class instance."""
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
        """Get configuration settings from configuration file."""
        options = get_config()
        self.output_dir = options.get('rsr_dir', './')
        self.path = options[self.platform_name + '-' + self.instrument]['path']
        self.options = options

    def _get_bandfilenames(self):
        """Get the instrument rsr filenames."""
        for band in self.bandnames:
            LOG.debug("Band = %s", str(band))
            self.filenames[band] = os.path.join(self.path,
                                                self.options[self.platform_name + '-' +
                                                             self.instrument][band])
            LOG.debug(self.filenames[band])
            if not os.path.exists(self.filenames[band]):
                LOG.warning("Couldn't find an existing file for this band: %s",
                            str(self.filenames[band]))

    def _load(self, scale=1.0):
        """Load the instrument RSR from file(s)."""
        raise NotImplementedError(
            "Instrument rsr loader needs to be defined in the subclass")
