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

"""Testing the radiance to brightness temperature conversion
"""

from pyspectral.radiance_tb_conversion import RadTbConverter
import unittest
import numpy as np


TEST_TBS = np.array([200., 270., 300., 302., 350.], dtype='float32')

TRUE_RADS = np.array([856.937353205, 117420.385297,
                      479464.582505, 521412.9511, 2928735.18944],
                     dtype='float64')

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


SEV_RSR = {'IR3.9': {}}
SEV_RSR['IR3.9']['det-1'] = {}
WAVN = np.array([2083.33325195, 2091.00048828, 2098.72387695, 2106.50488281,
                 2114.34375, 2122.24121094, 2130.19775391, 2138.21435547,
                 2146.29101562, 2154.42944336, 2162.62963867, 2170.89257812,
                 2179.21899414, 2187.609375, 2196.06494141, 2204.58569336,
                 2213.17285156, 2221.82714844, 2230.54956055, 2239.34082031,
                 2248.20141602, 2257.13256836, 2266.13500977, 2275.20947266,
                 2284.35668945, 2293.57788086, 2302.87402344, 2312.24584961,
                 2321.6940918, 2331.21972656, 2340.82421875, 2350.5078125,
                 2360.27197266, 2370.11743164, 2380.0456543, 2390.05737305,
                 2400.15356445, 2410.33544922, 2420.60449219, 2430.9609375,
                 2441.40625, 2451.94189453, 2462.5690918, 2473.28857422,
                 2484.10180664, 2495.01025391, 2506.01416016, 2517.11645508,
                 2528.31713867, 2539.61816406, 2551.02050781, 2562.52587891,
                 2574.13525391, 2585.8503418, 2597.67236328, 2609.60351562,
                 2621.64453125, 2633.796875, 2646.06274414, 2658.44335938,
                 2670.94018555, 2683.55541992, 2696.28979492, 2709.14624023,
                 2722.12548828, 2735.22973633, 2748.4609375, 2761.82055664,
                 2775.31103516, 2788.93359375, 2802.69042969, 2816.58422852,
                 2830.61621094, 2844.78833008, 2859.10351562, 2873.56323242,
                 2888.17016602, 2902.92626953, 2917.83374023, 2932.89550781,
                 2948.11328125, 2963.48999023, 2979.02758789, 2994.72924805,
                 3010.59741211, 3026.63452148, 3042.84326172, 3059.22705078,
                 3075.78735352, 3092.52880859, 3109.45263672, 3126.56323242,
                 3143.86328125, 3161.35571289, 3179.04394531, 3196.9309082,
                 3215.02050781, 3233.31640625, 3251.82104492, 3270.5390625],
                dtype='float32')

RESP = np.array([5.85991074e-07, 5.05963471e-05, 1.54738867e-04,
                 8.75972546e-07, 2.23005936e-05, 6.17855985e-05,
                 1.41724333e-04, 1.87453145e-06, 3.19355922e-06,
                 1.08511595e-04, 2.12896630e-04, 5.65914146e-04,
                 5.93333738e-04, 2.45316158e-04, 1.77410198e-04,
                 3.18188017e-04, 5.27926895e-05, 1.41405777e-04,
                 1.64295849e-03, 2.69834511e-03, 4.89762053e-03,
                 2.71760323e-03, 2.49398337e-03, 4.83754929e-03,
                 1.08462553e-02, 5.53890038e-03, 8.30772892e-03,
                 1.33131407e-02, 2.89320182e-02, 4.69624363e-02,
                 6.85162693e-02, 1.17517754e-01, 2.26854816e-01,
                 3.69935125e-01, 5.16705751e-01, 6.70479536e-01,
                 8.18419516e-01, 9.00036395e-01, 9.59491372e-01,
                 9.60837066e-01, 9.63596582e-01, 9.77563441e-01,
                 9.98380423e-01, 9.98030603e-01, 9.93735969e-01,
                 9.84225452e-01, 9.98880267e-01, 1.00000000e+00,
                 9.90870714e-01, 9.75207090e-01, 9.68391836e-01,
                 9.73213553e-01, 9.75407243e-01, 9.57278728e-01,
                 9.68693912e-01, 9.78199899e-01, 9.73649919e-01,
                 9.81804073e-01, 9.71176386e-01, 9.72167253e-01,
                 9.60459769e-01, 9.40638900e-01, 9.24033165e-01,
                 9.16043043e-01, 8.79902899e-01, 8.11953366e-01,
                 6.69838488e-01, 4.60774124e-01, 2.68200457e-01,
                 1.34857073e-01, 6.40064552e-02, 3.31763141e-02,
                 1.24335978e-02, 6.22070907e-03, 2.53354642e-03,
                 1.81269188e-05, 4.63075470e-03, 1.78873568e-04,
                 1.01367442e-03, 1.28920563e-03, 4.91134451e-05,
                 6.77187869e-04, 2.44393433e-03, 2.62995227e-03,
                 6.38825062e-04, 1.70478446e-03, 1.03909883e-03,
                 1.27910142e-04, 2.95412028e-04, 8.80619162e-04,
                 2.42782771e-04, 7.55985593e-06, 3.55220342e-04,
                 8.71264958e-04, 2.01994626e-04, 8.14358555e-06,
                 2.14082262e-04, 1.07610082e-04, 5.82974189e-06,
                 4.16795141e-04], dtype='float32')

SEV_RSR['IR3.9']['det-1']['wavenumber'] = WAVN
SEV_RSR['IR3.9']['det-1']['response'] = RESP


class ProductionClass(RadTbConverter):
    """Production class"""

    def get_rsr(self):
        """Get RSR"""
        self.rsr = TEST_RSR
        self._wave_unit = '1e-6 m'
        self._wave_si_scale = 1e-6


class SeviriClass(RadTbConverter):
    """Class for Seviri"""

    def get_rsr(self):
        """Get RSR"""
        self.rsr = SEV_RSR
        self._wave_unit = 'cm-1'
        self._wave_si_scale = 100.

class TestRadTbConversions(unittest.TestCase):
    """Testing the conversions between radiances and brightness temperatures"""

    def setUp(self):
        """Set up"""
        self.modis = ProductionClass('EOS-Terra', 'modis', '20', method=1)
        self.sev1 = SeviriClass('Meteosat-9', 'seviri', 'IR3.9',
                                method=1, wavespace='wavenumber')
        self.sev2 = ProductionClass('Meteosat-9', 'seviri', 'IR3.9',
                                    method=2)

    def test_rad2tb(self):
        """Unit testing the radiance to brightness temperature conversion"""
        res = self.modis.tb2radiance(TEST_TBS, '20', lut=False)
        self.assertTrue(np.allclose(TRUE_RADS, res['radiance']))

        res = self.modis.tb2radiance(237., '20', lut=False)
        self.assertAlmostEqual(16570.592171157, res['radiance'])

        res = self.modis.tb2radiance(277., '20', lut=False)
        self.assertAlmostEqual(167544.3823631, res['radiance'])

        res = self.modis.tb2radiance(1.1, '20', lut=False)
        self.assertAlmostEqual(0.0, res['radiance'])

        res = self.modis.tb2radiance(11.1, '20', lut=False)
        self.assertAlmostEqual(0.0, res['radiance'])

        res = self.modis.tb2radiance(100.1, '20', lut=False)
        self.assertAlmostEqual(5.3940515573e-06, res['radiance'])

        res = self.modis.tb2radiance(200.1, '20', lut=False)
        self.assertAlmostEqual(865.09776189, res['radiance'])

    def test_conversion_simple(self):
        """Test the tb2radiance_simple function to convert radiances to Tb's"""
        retv = self.sev2.tb2radiance_simple(TEST_TBS, 'IR3.9')
        rads = retv['radiance']
        # Units space = wavenumber (cm-1):
        tbs = self.sev2.radiance2tb_simple(rads, 'IR3.9')
        self.assertTrue(np.allclose(TEST_TBS, tbs))

        np.random.seed()
        tbs1 = 200.0 + np.random.random(50) * 150.0
        retv = self.sev2.tb2radiance_simple(tbs1, 'IR3.9')
        rads = retv['radiance']
        tbs = self.sev2.radiance2tb_simple(rads, 'IR3.9')
        self.assertTrue(np.allclose(tbs1, tbs))

    def test_conversions_methods(self):
        """Using the two diferent conversion methods to verify that they give
        approximately the same results. Conversion from Tb's to Radiances
        only
        """
        # Units space = wavenumber (cm-1):
        retv2 = self.sev2.tb2radiance_simple(TEST_TBS, 'IR3.9')
        retv1 = self.sev1.tb2radiance(TEST_TBS, 'IR3.9')

        rads1 = retv1['radiance']
        rads2 = retv2['radiance']
        self.assertTrue(np.allclose(rads1, rads2))

    def tearDown(self):
        """Clean up"""
        pass

def suite():
    """The suite for test_reflectance."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestRadTbConversions))

    return mysuite
