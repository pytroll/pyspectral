#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Adam.Dybbroe

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

"""Unit testing the Blackbody/Plack radiation derivation
"""

from pyspectral.blackbody import blackbody

import unittest
import numpy as np

RAD_11MICRON_300KELVIN = 9570997.121452963
RAD_11MICRON_301KELVIN = 9712482.1816418115

class Test(unittest.TestCase):
    """Unit testing the pps reading"""
           
    def setUp(self):
        """Set up"""
        return

    def test_blackbody(self):
        """Calculate the blackbody radiation from wavelengths and temperatures"""

        b = blackbody((11. * 1E-6, ), [300., 301])
        self.assertEqual(b.shape[0], 2)
        self.assertAlmostEqual(b[0], RAD_11MICRON_300KELVIN)
        self.assertAlmostEqual(b[1], RAD_11MICRON_301KELVIN)

        b = blackbody(13. * 1E-6, 200.)
        self.assertTrue(np.isscalar(b))

    def tearDown(self):
        """Clean up"""
        return

