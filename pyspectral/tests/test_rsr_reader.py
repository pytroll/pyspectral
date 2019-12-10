#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, 2018, 2019 Adam.Dybbroe

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

"""Unit testing the generic rsr hdf5 reader."""

import sys
import os.path
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import WAVE_NUMBER
from pyspectral.utils import RSR_DATA_VERSION
import numpy as np

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3,):
    from mock import patch
else:
    from unittest.mock import patch

TEST_RSR = {'20': {}, }
TEST_RSR['20']['det-1'] = {}
TEST_RSR['20']['det-1']['central_wavelength'] = 3.75
TEST_RSR['20']['det-1']['wavelength'] = np.array([
    3.6123999, 3.6163599, 3.6264927, 3.6363862, 3.646468,
    3.6564937, 3.6664478, 3.6765388, 3.6865413, 3.6964585,
    3.7065142, 3.716509, 3.7264658, 3.7364102, 3.7463682,
    3.7563652, 3.7664226, 3.7763396, 3.7863384, 3.7964207,
    3.8063589, 3.8163606, 3.8264089, 3.8364836, 3.8463381,
    3.8563975, 3.8664163, 3.8763755, 3.8864797, 3.8964978,
    3.9064275, 3.9164873, 3.9264729, 3.9364026, 3.9465107,
    3.9535347], dtype='float32')

TEST_RSR['20']['det-1']['response'] = np.array([
    0.01, 0.0118, 0.01987, 0.03226, 0.05028, 0.0849,
    0.16645, 0.33792, 0.59106, 0.81815, 0.96077, 0.92855,
    0.86008, 0.8661, 0.87697, 0.85412, 0.88922, 0.9541,
    0.95687, 0.91037, 0.91058, 0.94256, 0.94719, 0.94808,
    1., 0.92676, 0.67429, 0.44715, 0.27762, 0.14852,
    0.07141, 0.04151, 0.02925, 0.02085, 0.01414, 0.01], dtype='float32')

TEST_RSR2 = {'20': {}, }
TEST_RSR2['20']['det-1'] = {}
TEST_RSR2['20']['det-1']['central_wavelength'] = 3.75
TEST_RSR2['20']['det-1']['wavelength'] = TEST_RSR['20']['det-1']['wavelength'].copy()
TEST_RSR2['20']['det-1']['response'] = TEST_RSR['20']['det-1']['response'].copy()

RESULT_WVN_RSR = np.array([2529.38232422,  2533.8840332,  2540.390625,  2546.81494141,
                           2553.30859375,  2559.88378906,  2566.40722656,  2573.02270508,
                           2579.72949219,  2586.37451172,  2593.09375,  2599.87548828,
                           2606.55371094,  2613.41674805,  2620.29760742,  2627.18286133,
                           2634.06005859,  2641.07421875,  2648.06713867,  2655.03930664,
                           2662.14794922,  2669.25170898,  2676.36572266,  2683.50805664,
                           2690.69702148,  2697.95288086,  2705.29199219,  2712.56982422,
                           2719.94970703,  2727.43554688,  2734.8605957,  2742.37988281,
                           2749.9831543,  2757.48510742,  2765.21142578,  2768.24291992], dtype=np.float32)

DIR_PATH_ITEMS = ['test', 'path', 'to', 'rsr', 'data']
TEST_CONFIG = {}

TEST_RSR_DIR = os.path.join(*DIR_PATH_ITEMS)
TEST_CONFIG['rsr_dir'] = TEST_RSR_DIR


class TestRsrReader(unittest.TestCase):
    """Class for testing pyspectral.rsr_reader."""

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse.load')
    @patch('pyspectral.rsr_reader.download_rsr')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse._get_rsr_data_version')
    def test_rsr_response(self, get_rsr_version, download_rsr, load, isfile, exists):
        """Test the RelativeSpectralResponse class initialisation."""
        load.return_code = None
        download_rsr.return_code = None
        isfile.return_code = True
        exists.return_code = True
        get_rsr_version.return_code = RSR_DATA_VERSION

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            with self.assertRaises(AttributeError):
                test_rsr = RelativeSpectralResponse('GOES-16')
                test_rsr = RelativeSpectralResponse(instrument='ABI')

            test_rsr = RelativeSpectralResponse('GOES-16', 'AbI')
            self.assertEqual(test_rsr.platform_name, 'GOES-16')
            self.assertEqual(test_rsr.instrument, 'abi')
            test_rsr = RelativeSpectralResponse('GOES-16', 'ABI')
            self.assertEqual(test_rsr.instrument, 'abi')

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            test_rsr = RelativeSpectralResponse('GOES-16', 'abi')

        self.assertEqual(test_rsr.platform_name, 'GOES-16')
        self.assertEqual(test_rsr.instrument, 'abi')
        self.assertEqual(
            test_rsr.filename, os.path.join(TEST_RSR_DIR, 'rsr_abi_GOES-16.h5'))

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            test_rsr = RelativeSpectralResponse(
                filename=os.path.join(TEST_RSR_DIR, 'rsr_abi_GOES-16.h5'))

        self.assertEqual(
            test_rsr.filename, os.path.join(TEST_RSR_DIR, 'rsr_abi_GOES-16.h5'))

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse.load')
    @patch('pyspectral.rsr_reader.download_rsr')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse._get_rsr_data_version')
    def test_convert(self, get_rsr_version, download_rsr, load, isfile, exists):
        """Test the conversion method."""
        load.return_code = None
        download_rsr.return_code = None
        isfile.return_code = True
        exists.return_code = True
        get_rsr_version.return_code = RSR_DATA_VERSION

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            test_rsr = RelativeSpectralResponse('EOS-Aqua', 'modis')
            test_rsr.rsr = TEST_RSR
            test_rsr.convert()
            self.assertAlmostEqual(test_rsr.rsr['20']['det-1']['central_wavenumber'], 2647.397, 3)
            self.assertTrue(np.allclose(test_rsr.rsr['20']['det-1'][WAVE_NUMBER], RESULT_WVN_RSR, 5))
            self.assertEqual(test_rsr._wavespace, WAVE_NUMBER)

            with self.assertRaises(NotImplementedError):
                test_rsr.convert()

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse.load')
    @patch('pyspectral.rsr_reader.download_rsr')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse._get_rsr_data_version')
    def test_integral(self, get_rsr_version, download_rsr, load, isfile, exists):
        """Test the calculation of the integral of the spectral responses."""
        load.return_code = None
        download_rsr.return_code = None
        isfile.return_code = True
        exists.return_code = True
        get_rsr_version.return_code = RSR_DATA_VERSION

        with patch('pyspectral.rsr_reader.get_config', return_value=TEST_CONFIG):
            test_rsr = RelativeSpectralResponse('EOS-Aqua', 'modis')
            test_rsr.rsr = TEST_RSR2
            res = test_rsr.integral('20')
            self.assertAlmostEqual(res['det-1'], 0.185634, 6)
