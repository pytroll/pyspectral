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

"""Unit testing the solar_flux calculations"""

from pyspectral.solar import (SolarIrradianceSpectrum,
                              TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)

import os
import unittest
import numpy as np

TEST_RSR = {}
TEST_RSR['det-1'] = {}
TEST_RSR['det-1']['wavelength'] = np.array([
    3.6123999, 3.6163599, 3.6264927, 3.6363862, 3.646468,
    3.6564937, 3.6664478, 3.6765388, 3.6865413, 3.6964585,
    3.7065142, 3.716509, 3.7264658, 3.7364102, 3.7463682,
    3.7563652, 3.7664226, 3.7763396, 3.7863384, 3.7964207,
    3.8063589, 3.8163606, 3.8264089, 3.8364836, 3.8463381,
    3.8563975, 3.8664163, 3.8763755, 3.8864797, 3.8964978,
    3.9064275, 3.9164873, 3.9264729, 3.9364026, 3.9465107,
    3.9535347], dtype='double')

TEST_RSR['det-1']['response'] = np.array([
    0.01, 0.0118, 0.01987, 0.03226, 0.05028, 0.0849,
    0.16645, 0.33792, 0.59106, 0.81815, 0.96077, 0.92855,
    0.86008, 0.8661, 0.87697, 0.85412, 0.88922, 0.9541,
    0.95687, 0.91037, 0.91058, 0.94256, 0.94719, 0.94808,
    1., 0.92676, 0.67429, 0.44715, 0.27762, 0.14852,
    0.07141, 0.04151, 0.02925, 0.02085, 0.01414, 0.01], dtype='double')


class TestSolarflux(unittest.TestCase):

    """Unit testing the solar flux calculations"""

    def setUp(self):
        """Set up"""
        self.solar_irr = None
        self.rsr = TEST_RSR
        return

    def test_read(self):
        """Test that solar irradiance spctrum"""
        self.solar_irr = \
            SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM,
                                    dlambda=0.005)
        self.assertTrue(os.path.exists(self.solar_irr.filename))

        self.assertEqual(self.solar_irr.wavelength.shape[0], 1697)
        self.assertEqual(self.solar_irr.irradiance.shape[0], 1697)

    def test_solar_flux(self):
        """Calculate the solar-flux"""
        self.solar_irr = \
            SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM,
                                    dlambda=0.005)

        # rsr function (se above) is given in micronsm therefore the scale
        # factor is 1.0 and not 1e+6 (default)!
        sflux = self.solar_irr.inband_solarflux(self.rsr, scale=1.0)
        self.assertAlmostEqual(sflux, 2.0029277645144234)
        #self.assertAlmostEqual(sflux, 2.5)

    def tearDown(self):
        """Clean up"""
        return


def suite():
    """The suite for test_solarflux."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestSolarflux))

    return mysuite
