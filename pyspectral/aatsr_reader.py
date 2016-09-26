#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

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

"""Interface to the original Envisat AATSR spectral response functions from
ESA: http://envisat.esa.int/handbooks/aatsr/aux-files/consolidatedsrfs.xls

"""
import ConfigParser
import os
from xlrd import open_workbook
import numpy as np

from pyspectral.utils import convert2hdf5 as tohdf5


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

AATSR_BAND_NAMES = ['ir12', 'ir11', 'ir37', 'v16', 'v870', 'v659', 'v555']


class AatsrRSR(object):

    """Class for Envisat AATSR RSR"""

    def __init__(self, bandname, platform_name='Envisat'):
        """
        Read the aatsr relative spectral responses for all channels.

        """
        self.platform_name = platform_name
        self.instrument = 'aatsr'
        self.bandname = bandname
        self.rsr = None

        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception('Failed reading configuration file: %s',
                          str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items(self.platform_name + '-aatsr',
                                        raw=True):
            options[option] = value

        self.aatsr_path = options.get('path')

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')

        self._load()

    def _load(self, filename=None):
        """Read the AATSR rsr data"""
        if not filename:
            filename = self.aatsr_path

        wb_ = open_workbook(filename)

        for sheet in wb_.sheets():
            ch_name = sheet.name.strip()
            if ch_name == 'aatsr_' + self.bandname:

                data = np.array([s.split() for s in
                                 sheet.col_values(0,
                                                  start_rowx=3, end_rowx=258)])
                data = data.astype('f')
                wvl = data[:, 0]
                resp = data[:, 1]

                self.rsr = {'wavelength': wvl, 'response': resp}


def main():
    """Main"""

    tohdf5(AatsrRSR, 'Envisat', AATSR_BAND_NAMES)

if __name__ == "__main__":
    main()
