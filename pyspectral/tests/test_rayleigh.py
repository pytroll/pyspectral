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

"""Unittest for the rayleigh correction utilities
"""

import unittest
import sys
import numpy as np
import pyspectral.rsr_reader
from pyspectral import rayleigh
from pyspectral.rayleigh import BandFrequencyOutOfRange

from mock import patch

# Mock some modules, so we don't need them for tests.

#sys.modules['pyresample'] = MagicMock()


class rsrTestData(object):

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


class TestRayleigh(unittest.TestCase):

    """Class for testing pyspectral.rayleigh
    """

    def setUp(self):
        """Setup the test.
        """
        self.rsr = rsrTestData()

    def test_get_bandname_from_wavelength(self):

        x = rayleigh.get_bandname_from_wavelength(0.4, self.rsr)
        self.assertEqual(x, 'ch1')
        x = rayleigh.get_bandname_from_wavelength(0.5, self.rsr)
        self.assertEqual(x, 'ch2')
        x = rayleigh.get_bandname_from_wavelength(0.6, self.rsr)
        self.assertEqual(x, 'ch3')
        x = rayleigh.get_bandname_from_wavelength(0.7, self.rsr)
        self.assertEqual(x, 'ch3')
        x = rayleigh.get_bandname_from_wavelength(0.8, self.rsr)
        self.assertEqual(x, 'ch4')
        x = rayleigh.get_bandname_from_wavelength(1.0, self.rsr)
        self.assertEqual(x, None)

    def test_get_effective_wavelength(self):

        # mymock:
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = rsrTestData().rsr

            this = rayleigh.Rayleigh('Himawari-8', 'ahi')
            with self.assertRaises(BandFrequencyOutOfRange):
                this.get_effective_wavelength(0.9)

            # Only ch3 (~0.63) testdata implemented yet...
            x = this.get_effective_wavelength(0.7)
            self.assertAlmostEqual(x, 0.6356167)
            x = this.get_effective_wavelength(0.6)
            self.assertAlmostEqual(x, 0.6356167)

        # mymock:
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.side_effect = IOError(
                'Fake that there is no spectral response file...')

            this = rayleigh.Rayleigh('Himawari-8', 'ahi')
            x = this.get_effective_wavelength(0.7)
            self.assertEqual(x, 0.7)
            x = this.get_effective_wavelength(0.9)
            self.assertEqual(x, 0.9)
            x = this.get_effective_wavelength(0.455)
            self.assertEqual(x, 0.455)

    def tearDown(self):
        """Clean up"""
        pass


def suite():
    """The test suite for test_rayleigh.
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestRayleigh))

    return mysuite
