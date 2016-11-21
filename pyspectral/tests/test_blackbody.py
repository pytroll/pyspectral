#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014, 2015, 2016 Adam.Dybbroe

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

"""Unit testing the Blackbody/Plack radiation derivation"""

from pyspectral.blackbody import (blackbody, blackbody_wn,
                                  blackbody_wn_rad2temp,
                                  blackbody_rad2temp)

import unittest
import numpy as np

#RAD_11MICRON_300KELVIN = 9572498.1141643394
RAD_11MICRON_300KELVIN = 9573177.8811719529
#RAD_11MICRON_301KELVIN = 9713997.9623772576
RAD_11MICRON_301KELVIN = 9714688.2959563732

# Radiances in wavenumber space (SI-units)
WN_RAD_11MICRON_300KELVIN = 0.00115835441353
WN_RAD_11MICRON_301KELVIN = 0.00117547716523

__unittest = True


def assertNumpyArraysEqual(self, other):
    if self.shape != other.shape:
        raise AssertionError("Shapes don't match")
    if not np.allclose(self, other):
        raise AssertionError("Elements don't match!")


class TestBlackbody(unittest.TestCase):

    """Unit testing the blackbody function"""

    def setUp(self):
        """Set up"""
        return

    def test_blackbody(self):
        """Calculate the blackbody radiation from wavelengths and
        temperatures
        """
        wavel = 11. * 1E-6
        black = blackbody((wavel, ), [300., 301])
        self.assertEqual(black.shape[0], 2)
        self.assertAlmostEqual(black[0], RAD_11MICRON_300KELVIN)
        self.assertAlmostEqual(black[1], RAD_11MICRON_301KELVIN)

        temp1 = blackbody_rad2temp(wavel, black[0])
        self.assertAlmostEqual(temp1, 300.0, 4)
        temp2 = blackbody_rad2temp(wavel, black[1])
        self.assertAlmostEqual(temp2, 301.0, 4)

        black = blackbody(13. * 1E-6, 200.)
        self.assertTrue(np.isscalar(black))

        tb_therm = np.array([[300., 301], [299, 298], [279, 286]])
        black = blackbody((10. * 1E-6, 11.e-6), tb_therm)

        tb_therm = np.array([[300., 301], [0., 298], [279, 286]])
        black = blackbody((10. * 1E-6, 11.e-6), tb_therm)

    def test_blackbody_wn(self):
        """Calculate the blackbody radiation from wavenumbers and
        temperatures
        """
        wavenumber = 90909.1  # 11 micron band
        black = blackbody_wn((wavenumber, ), [300., 301])
        print black
        self.assertEqual(black.shape[0], 2)
        self.assertAlmostEqual(black[0], WN_RAD_11MICRON_300KELVIN)
        self.assertAlmostEqual(black[1], WN_RAD_11MICRON_301KELVIN)

        temp1 = blackbody_wn_rad2temp(wavenumber, black[0])
        self.assertAlmostEqual(temp1, 300.0, 4)
        temp2 = blackbody_wn_rad2temp(wavenumber, black[1])
        self.assertAlmostEqual(temp2, 301.0, 4)

        t__ = blackbody_wn_rad2temp(wavenumber, [0.001, 0.0009])
        expected = [290.3276916, 283.76115441]
        self.assertAlmostEqual(t__[0], expected[0])
        self.assertAlmostEqual(t__[1], expected[1])

        radiances = np.array([0.001, 0.0009, 0.0012, 0.0018]).reshape(2, 2)
        t__ = blackbody_wn_rad2temp(wavenumber, radiances)
        expected = np.array([290.3276916, 283.76115441,
                             302.4181330, 333.1414164]).reshape(2, 2)
        self.assertAlmostEqual(t__[1, 1], expected[1, 1], 5)
        self.assertAlmostEqual(t__[0, 0], expected[0, 0], 5)
        self.assertAlmostEqual(t__[0, 1], expected[0, 1], 5)
        self.assertAlmostEqual(t__[1, 0], expected[1, 0], 5)

        assertNumpyArraysEqual(t__, expected)

    def tearDown(self):
        """Clean up"""
        return


def suite():
    """The suite for test_blackbody."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestBlackbody))

    return mysuite
