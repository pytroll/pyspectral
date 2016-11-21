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

import datetime
import unittest
import sys
import pyspectral.rsr_reader
from pyspectral import rayleigh
from pyspectral.rayleigh import BandFrequencyOutOfRange

from mock import patch, MagicMock

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
        idx = 0
        for chname in channel_names:
            self.rsr[chname] = {'det-1': {}}
            self.rsr[chname]['det-1']['central_wavelength'] = wvl[idx]
            idx = idx + 1


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

    # def test_get_effective_wavelength(self):

    #     with patch('pyspectral.rsr_reader.RelativeSpectralResponse') as mymock:
    #         instance = mymock.return_value
    #         instance.rsr = rsrTestData().rsr

    #         import pdb
    #         pdb.set_trace()

    #         this = rayleigh.Rayleigh('Himawari-8', 'ahi')
    #         with self.assertRaises(BandFrequencyOutOfRange):
    #             this.get_effective_wavelength(0.9)

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
