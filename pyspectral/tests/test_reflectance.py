#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014, 2015 Adam.Dybbroe

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

"""Unit testing the 3.7 micron reflectance calculations"""

from pyspectral.near_infrared_reflectance import Calculator

import unittest
import numpy as np

TEST_RSR = {'20': {}}
TEST_RSR['20']['det-1'] = {}
TEST_RSR['20']['det-1']['wavelength'] = np.array([
    3.6123999, 3.6163599, 3.6264927, 3.6363862, 3.646468,
    3.6564937, 3.6664478, 3.6765388, 3.6865413, 3.6964585,
    3.7065142, 3.716509, 3.7264658, 3.7364102, 3.7463682,
    3.7563652, 3.7664226, 3.7763396, 3.7863384, 3.7964207,
    3.8063589, 3.8163606, 3.8264089, 3.8364836, 3.8463381,
    3.8563975, 3.8664163, 3.8763755, 3.8864797, 3.8964978,
    3.9064275, 3.9164873, 3.9264729, 3.9364026, 3.9465107,
    3.9535347], dtype='double')

TEST_RSR['20']['det-1']['response'] = np.array([
    0.01, 0.0118, 0.01987, 0.03226, 0.05028, 0.0849,
    0.16645, 0.33792, 0.59106, 0.81815, 0.96077, 0.92855,
    0.86008, 0.8661, 0.87697, 0.85412, 0.88922, 0.9541,
    0.95687, 0.91037, 0.91058, 0.94256, 0.94719, 0.94808,
    1., 0.92676, 0.67429, 0.44715, 0.27762, 0.14852,
    0.07141, 0.04151, 0.02925, 0.02085, 0.01414, 0.01], dtype='double')

TEST_RSR_WN = {'20': {}}
TEST_RSR_WN['20']['det-1'] = {}
WVN = np.array([2529.38208008, 2533.8840332, 2540.390625, 2546.81494141,
                2553.30883789, 2559.88354492, 2566.40722656, 2573.02270508,
                2579.72949219, 2586.37451172, 2593.09375, 2599.87548828,
                2606.55371094, 2613.41674805, 2620.29760742, 2627.18286133,
                2634.06005859, 2641.07421875, 2648.06713867, 2655.03930664,
                2662.14794922, 2669.25170898, 2676.36572266, 2683.50805664,
                2690.69702148, 2697.95288086, 2705.29199219, 2712.56982422,
                2719.94970703, 2727.43554688, 2734.8605957, 2742.38012695,
                2749.9831543, 2757.48510742, 2765.21142578, 2768.24291992],
               dtype='float32')
RESP = np.array([0.01, 0.01414, 0.02085, 0.02925, 0.04151,
                 0.07141, 0.14851999, 0.27761999, 0.44714999, 0.67429,
                 0.92676002, 1., 0.94808, 0.94718999, 0.94256002,
                 0.91057998, 0.91036999, 0.95687002, 0.95410001, 0.88922,
                 0.85412002, 0.87696999, 0.86610001, 0.86008, 0.92855,
                 0.96077001, 0.81814998, 0.59105998, 0.33792001, 0.16644999,
                 0.0849, 0.05028, 0.03226, 0.01987, 0.0118,
                 0.01], dtype='float32')

TEST_RSR_WN['20']['det-1']['wavenumber'] = WVN
TEST_RSR_WN['20']['det-1']['response'] = RESP


class ProductionClass(Calculator):
    """ProductionClass"""

    def get_rsr(self):
        self.rsr = TEST_RSR
        self._wave_unit = '1e-6 m'
        self._wave_si_scale = 1e-6

class ProductionClassWN(Calculator):
    """Wrapper for wavenumber calculations..."""

    def __init__(self, platform_name, instrument, bandname,
                 solar_flux=None, **options):
        self.wavespace = 'wavenumber'
        self.get_rsr()
        super(ProductionClassWN, self).__init__(platform_name, instrument,
                                                bandname, solar_flux=None,
                                                **options)

    def get_rsr(self):
        """Get RSR"""
        self.rsr = TEST_RSR_WN
        self._wave_unit = 'cm-1'
        self._wave_si_scale = 100.


class TestReflectance(unittest.TestCase):

    """Unit testing the reflectance calculations"""

    def setUp(self):
        """Set up"""
        pass

    def test_rsr_integral(self):
        """Test calculating the integral of the relative spectral response
        function. 
        """
        refl37 = ProductionClass('EOS-Aqua', 'modis', '20')
        expected = 0.18563451
        self.assertAlmostEqual(refl37.rsr_integral, expected)

        refl37 = ProductionClassWN(
            'EOS-Aqua', 'modis', '20', wavespace='wavenumber')
        expected = 130.0039
        self.assertAlmostEqual(refl37.rsr_integral, expected, 4)

    def test_reflectance(self):
        """Test the derivation of the reflective part of a 3.7 micron band"""
        refl37 = ProductionClass('EOS-Aqua', 'modis', '20')

        sunz = 80.
        tb3 = 290.
        tb4 = 282.
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        self.assertAlmostEqual(refl, 0.25124494860154067) #0.251245010648)

        sunz = 80.
        tb3 = 295.
        tb4 = 282.
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        self.assertAlmostEqual(refl, 0.452497961)

        sunz = 50.
        tb3 = 300.
        tb4 = 285.
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        self.assertAlmostEqual(refl, 0.1189217)

    def tearDown(self):
        """Clean up"""
        pass

def suite():
    """The suite for test_reflectance.
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestReflectance))

    return mysuite
