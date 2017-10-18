#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Adam.Dybbroe

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

"""Test the raw satellite instrument rsr readers."""

import sys
import mock
from pyspectral.aatsr_reader import AatsrRSR

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

AATSR_PATH = '/home/a000680/data/SpectralResponses/aatsr/consolidatedsrfs.xls'
RSR_DIR = '/home/a000680/data/pyspectral'


class TestAatsrRsrReader(unittest.TestCase):

    """Test the rsr reader for the Envisat AATSR"""

    @mock.patch('xlrd.open_workbook')
    @mock.patch('pyspectral.aatsr_reader.AatsrRSR._load')
    @mock.patch('pyspectral.config.get_config')
    def setUp(self, get_config, _load, open_workbook):
        """Setup the natve MSG file handler for testing."""
        open_workbook.return_code = None
        get_config.return_code = {}
        _load.return_code = None

        self.rsr_reader = AatsrRSR('ir12', 'Envisat')
        self.rsr_reader.aatsr_path = AATSR_PATH
        self.rsr_dir = RSR_DIR
        self._open_wb = open_workbook.return_code

    def test_load(self):
        """Test the loading of the rsr data"""
        pass

    def tearDown(self):
        """Clean up"""


def suite():
    """The test suite for test_scene."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestAatsrRsrReader))
    return mysuite

if __name__ == "__main__":
    # So you can run tests from this module individually.
    unittest.main()
