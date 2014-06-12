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

"""Unittests for the utils library
"""

from pyspectral import utils

import unittest
import numpy as np

TEST_RSR = {'20': {}}
TEST_RSR['20']['det-1'] = {}
TEST_RSR['20']['det-1']['wavelength'] = np.array([
        3.6123999,  3.6163599,  3.6264927,  3.6363862,  3.646468 ,
        3.6564937,  3.6664478,  3.6765388,  3.6865413,  3.6964585,
        3.7065142,  3.716509 ,  3.7264658,  3.7364102,  3.7463682,
        3.7563652,  3.7664226,  3.7763396,  3.7863384,  3.7964207,
        3.8063589,  3.8163606,  3.8264089,  3.8364836,  3.8463381,
        3.8563975,  3.8664163,  3.8763755,  3.8864797,  3.8964978,
        3.9064275,  3.9164873,  3.9264729,  3.9364026,  3.9465107,
        3.9535347], dtype='double') * 1e-6

TEST_RSR['20']['det-1']['response'] = np.array([
        0.01   ,  0.0118 ,  0.01987,  0.03226,  0.05028,  0.0849 ,
        0.16645,  0.33792,  0.59106,  0.81815,  0.96077,  0.92855,
        0.86008,  0.8661 ,  0.87697,  0.85412,  0.88922,  0.9541 ,
        0.95687,  0.91037,  0.91058,  0.94256,  0.94719,  0.94808,
        1.     ,  0.92676,  0.67429,  0.44715,  0.27762,  0.14852,
        0.07141,  0.04151,  0.02925,  0.02085,  0.01414,  0.01 ], dtype='double')

RESULT_RSR = {'20': {}}
RESULT_RSR['20']['det-1'] = {}
RESULT_RSR['20']['det-1']['wavenumber'] = np.array([
        2529.38212481,  2533.88391928,  2540.39055863,  2546.81497993,
        2553.30842002,  2559.88367889,  2566.40719777,  2573.02257362,
        2579.72944056,  2586.37436429,  2593.09368394,  2599.87545037,
        2606.55356379,  2613.41645949,  2620.2974635 ,  2627.18263378,
        2634.06002396,  2641.0740255 ,  2648.06692703,  2655.03929379,
        2662.14797219,  2669.25178363,  2676.36567313,  2683.50778907,
        2690.69710311,  2697.95270176,  2705.29210594,  2712.5696381 ,
        2719.94953514,  2727.43553038,  2734.86044841,  2742.37974939,
        2749.98293636,  2757.4852143 ,  2765.21150453,  2768.24279615])

RESULT_RSR['20']['det-1']['response'] = np.array([
        0.01   ,  0.01414,  0.02085,  0.02925,  0.04151,  0.07141,
        0.14852,  0.27762,  0.44715,  0.67429,  0.92676,  1.     ,
        0.94808,  0.94719,  0.94256,  0.91058,  0.91037,  0.95687,
        0.9541 ,  0.88922,  0.85412,  0.87697,  0.8661 ,  0.86008,
        0.92855,  0.96077,  0.81815,  0.59106,  0.33792,  0.16645,
        0.0849 ,  0.05028,  0.03226,  0.01987,  0.0118 ,  0.01   ])


class TestUtils(unittest.TestCase):
    """Unit testing the utils library functions"""
           
    def setUp(self):
        """Set up"""

    def test_convert2wavenumber(self):
        """Testing the conversion of rsr from wavelength to wavenumber"""

        newrsr, unit = utils.convert2wavenumber(TEST_RSR)
        
        self.assertEqual(unit, 'cm-1')
        self.assertTrue(newrsr['20']['det-1'].has_key('wavenumber'))
        self.assertFalse(newrsr['20']['det-1'].has_key('wavelength'))

        wvn_res = RESULT_RSR['20']['det-1']['wavenumber']
        wvn = newrsr['20']['det-1']['wavenumber']
        self.assertTrue(np.allclose(wvn_res, wvn))


    def tearDown(self):
        """Clean up"""


def suite():
    """The suite for test_utils.
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestUtils))
    
    return mysuite
