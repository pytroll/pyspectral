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

"""Unit testing the generic rsr hdf5 reader
"""
import sys
from pyspectral.rsr_reader import RelativeSpectralResponse
from mock import patch
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


TEST_CONFIG = {}
TEST_CONFIG['rsr_dir'] = '/test/path/to/rsr/data'


class TestRsrReader(unittest.TestCase):

    """Class for testing pyspectral.rsr_reader"""

    def setUp(self):
        """Setup the test"""
        pass

    @mock.patch('os.path.exists')
    @mock.patch('os.path.isfile')
    @mock.patch('pyspectral.rsr_reader.RelativeSpectralResponse.load')
    @mock.patch('pyspectral.rsr_reader.download_rsr')
    def test_rsr_reponse(self, download_rsr, load, isfile, exists):
        """Test the relative_"""
        load.return_code = None
        download_rsr.return_code = None
        isfile.return_code = True
        exists.return_code = True

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            test_rsr = RelativeSpectralResponse('GOES-16', 'abi')

        self.assertEqual(test_rsr.platform_name, 'GOES-16')
        self.assertEqual(test_rsr.instrument, 'abi')
        self.assertEqual(
            test_rsr.filename, '/test/path/to/rsr/data/rsr_abi_GOES-16.h5')

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            test_rsr = RelativeSpectralResponse(
                filename='/test/path/to/rsr/data/rsr_abi_GOES-16.h5')

        self.assertEqual(
            test_rsr.filename, '/test/path/to/rsr/data/rsr_abi_GOES-16.h5')

    def tearDown(self):
        """Clean up"""
        pass


def suite():
    """The test suite for test_rsr_reader.
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestRsrReader))

    return mysuite
