#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2017, 2018 Adam.Dybbroe

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

"""Unittests for the utils library"""

from pyspectral import utils

import unittest
import numpy as np

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

RESULT_RSR = {'20': {}}
RESULT_RSR['20']['det-1'] = {}
RESULT_RSR['20']['det-1']['wavenumber'] = np.array([
    2529.38208008, 2533.8840332, 2540.390625, 2546.81494141,
    2553.30883789, 2559.88354492, 2566.40722656, 2573.02270508,
    2579.72949219, 2586.37451172, 2593.09375, 2599.87548828,
    2606.55371094, 2613.41674805, 2620.29760742, 2627.18286133,
    2634.06005859, 2641.07421875, 2648.06713867, 2655.03930664,
    2662.14794922, 2669.25170898, 2676.36572266, 2683.50805664,
    2690.69702148, 2697.95288086, 2705.29199219, 2712.56982422,
    2719.94970703, 2727.43554688, 2734.8605957, 2742.38012695,
    2749.9831543, 2757.48510742, 2765.21142578, 2768.24291992],
    dtype='float32')

RESULT_RSR['20']['det-1']['response'] = np.array([
    0.01, 0.01414, 0.02085, 0.02925, 0.04151, 0.07141,
    0.14852, 0.27762, 0.44715, 0.67429, 0.92676, 1.,
    0.94808, 0.94719, 0.94256, 0.91058, 0.91037, 0.95687,
    0.9541, 0.88922, 0.85412, 0.87697, 0.8661, 0.86008,
    0.92855, 0.96077, 0.81815, 0.59106, 0.33792, 0.16645,
    0.0849, 0.05028, 0.03226, 0.01987, 0.0118, 0.01],
    dtype='float32')


class RsrTestData(object):

    """Container for the RSR test datasets"""

    def __init__(self):
        self.rsr = {}
        channel_names = ['ch12', 'ch13', 'ch10', 'ch11', 'ch16', 'ch14',
                         'ch15', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6',
                         'ch7', 'ch8', 'ch9']
        wvl = [9.6372744012936646, 10.407492196078628, 7.3468642293967275,
               8.5926867614178715, 13.280724258676756, 11.239642285822033,
               12.380741429961382, 0.47063607733748003, 0.5099976405799187,
               0.63914891611559055, 0.85668832355426627, 1.6100814361999056,
               2.2568056299864101, 3.8853663735353847, 6.2428987228916233,
               6.9411756334211789]
        ch3_wvl = np.array([0.55518544, 0.56779468, 0.58099002, 0.59481323, 0.60931027,
                            0.62453163, 0.64053291, 0.65737575, 0.67512828, 0.69386619,
                            0.71367401])
        ch3_resp = np.array([2.61000005e-05, 1.07899999e-04, 3.26119992e-03,
                             2.90650606e-01, 9.02460396e-01, 9.60878074e-01,
                             9.97266889e-01, 9.94823873e-01, 7.18220174e-01,
                             8.31819978e-03, 9.34999989e-05])

        idx = 0
        for chname in channel_names:
            self.rsr[chname] = {'det-1': {}}
            self.rsr[chname]['det-1']['central_wavelength'] = wvl[idx]
            idx = idx + 1

        chname = 'ch3'
        self.rsr[chname]['det-1']['wavelength'] = ch3_wvl
        self.rsr[chname]['det-1']['response'] = ch3_resp


class TestUtils(unittest.TestCase):

    """Unit testing the utils library functions"""

    def setUp(self):
        """Set up"""
        self.rsr = RsrTestData()

    def test_convert2wavenumber(self):
        """Testing the conversion of rsr from wavelength to wavenumber
        """
        newrsr, info = utils.convert2wavenumber(TEST_RSR)
        unit = info['unit']
        self.assertEqual(unit, 'cm-1')
        self.assertTrue('wavenumber' in newrsr['20']['det-1'])
        self.assertFalse('wavelength' in newrsr['20']['det-1'])
        wvn_res = RESULT_RSR['20']['det-1']['wavenumber']
        wvn = newrsr['20']['det-1']['wavenumber']
        self.assertTrue(np.allclose(wvn_res, wvn))

    def test_get_bandname_from_wavelength(self):
        """Test that it is possible to get the right bandname provided the wavelength
        in micro meters

        """

        x = utils.get_bandname_from_wavelength('abi', 0.4, self.rsr.rsr)
        self.assertEqual(x, 'ch1')
        with self.assertRaises(AttributeError):
            x = utils.get_bandname_from_wavelength('abi', 0.5, self.rsr.rsr)

        x = utils.get_bandname_from_wavelength('abi', 0.6, self.rsr.rsr, epsilon=0.05)
        self.assertEqual(x, 'ch3')
        x = utils.get_bandname_from_wavelength('abi', 0.7, self.rsr.rsr)
        self.assertEqual(x, 'ch3')
        x = utils.get_bandname_from_wavelength('abi', 0.8, self.rsr.rsr)
        self.assertEqual(x, 'ch4')
        x = utils.get_bandname_from_wavelength('abi', 1.0, self.rsr.rsr)
        self.assertEqual(x, None)

        bandname = utils.get_bandname_from_wavelength('abi', 3.7, TEST_RSR)
        self.assertEqual(bandname, '20')

        bandname = utils.get_bandname_from_wavelength('abi', 3.0, TEST_RSR)
        self.assertIsNone(bandname)

    def tearDown(self):
        """Clean up"""
        pass


def suite():
    """The suite for test_utils."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestUtils))

    return mysuite
