#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014-2019 Adam.Dybbroe

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

"""Testing the radiance to brightness temperature conversion."""

from pyspectral.radiance_tb_conversion import RadTbConverter
from pyspectral.radiance_tb_conversion import SeviriRadTbConverter
from pyspectral.utils import get_central_wave
import numpy as np
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
if sys.version_info < (3,):
    from mock import patch
else:
    from unittest.mock import patch


TEST_TBS = np.array([200., 270., 300., 302., 350.], dtype='float32')

TRUE_RADS = np.array([856.937353205, 117420.385297,
                      479464.582505, 521412.9511, 2928735.18944],
                     dtype='float64')
TRUE_RADS_SEVIRI = np.array([2.391091e-08,
                             2.559173e-06,
                             9.797091e-06,
                             1.061431e-05,
                             5.531423e-05],
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

TEST_RSR['20']['det-1']['central_wavelength'] = get_central_wave(TEST_RSR['20']['det-1']['wavelength'],
                                                                 TEST_RSR['20']['det-1']['response'])


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

VIIRS_RSR = {'I04': {}}
VIIRS_RSR['I04']['det-1'] = {}
I4_WAVELENGTH = np.array([0.0833394,  0.1022195,  0.130236,  0.16001581,  0.19955561,
                          0.24286181,  0.29621401,  0.35013291,  0.41273189,  0.47668689,
                          0.54601961,  0.59299731,  0.64459503,  0.67387378,  0.71287841,
                          0.74619591,  0.7725302,  0.7957828,  0.79547352,  0.82856262,
                          0.82099879,  0.83992928,  0.84202057,  0.84400982,  0.83308381,
                          0.85475749,  0.83983958,  0.84575808,  0.84324688,  0.84332639,
                          0.82304168,  0.83476579,  0.83626682,  0.82226139,  0.82139379,
                          0.81928378,  0.82413059,  0.8331368,  0.84240448,  0.858217,
                          0.86793423,  0.88952613,  0.91635668,  0.92613328,  0.92169321,
                          0.94074869,  0.94403398,  0.95178741,  0.95512831,  0.96271777,
                          0.965684,  0.94473231,  0.95947689,  0.94794488,  0.93577278,
                          0.91731572,  0.8803544,  0.86248928,  0.86056131,  0.86297452,
                          0.88312691,  0.91132039,  0.94761842,  0.96859932,  0.97495008,
                          0.97335148,  0.9552781,  0.98041701,  0.97318149,  0.97128302,
                          0.9795289,  0.97638869,  0.98553509,  0.97625399,  0.98542649,
                          0.98815048,  0.99496758,  0.98651272,  0.97830129,  0.95645708,
                          0.95295483,  0.91510731,  0.93925321,  0.9297964,  0.93927532,
                          0.942056,  0.95784009,  0.96388292,  0.96057928,  0.97130299,
                          0.98001093,  0.9716453,  0.96652049,  0.97841442,  0.96985549,
                          0.97240448,  1.,  0.99910343,  0.99543452,  0.98577332,
                          0.94873059,  0.91984153,  0.85985827,  0.78354579,  0.71279228,
                          0.60751349,  0.50684202,  0.41465551,  0.33605599,  0.2688629,
                          0.2085918,  0.1671019,  0.1307321,  0.1050327,  0.0833778],
                         dtype='float32')
I4_RESPONSE = np.array([3.51000977,  3.51399684,  3.51799059,  3.52198982,  3.52599406,
                        3.53000283,  3.53401518,  3.53803015,  3.54204679,  3.54595184,
                        3.54996943,  3.55398607,  3.55800128,  3.56201053,  3.56601906,
                        3.5700233,  3.57402253,  3.57790327,  3.58199954,  3.58597946,
                        3.58995199,  3.59402514,  3.59798145,  3.60203815,  3.60597777,
                        3.60990882,  3.61404991,  3.61796427,  3.62197948,  3.62598753,
                        3.62998843,  3.63398266,  3.63797164,  3.64195538,  3.64604282,
                        3.65001845,  3.65399408,  3.65796638,  3.66193819,  3.66601968,
                        3.66999412,  3.67408037,  3.67806101,  3.68194032,  3.68593097,
                        3.69003725,  3.69404101,  3.69805193,  3.70196342,  3.70599008,
                        3.70991707,  3.71407032,  3.71801329,  3.72207284,  3.72603106,
                        3.7299962,  3.73396754,  3.73805571,  3.74203897,  3.74602699,
                        3.75001884,  3.75401402,  3.75789952,  3.76200795,  3.76600695,
                        3.77000499,  3.77400184,  3.7779963,  3.78209734,  3.78597236,
                        3.7899549,  3.79393172,  3.79801106,  3.80197453,  3.80603933,
                        3.80998778,  3.81403589,  3.81796741,  3.8219986,  3.82602286,
                        3.8300364,  3.83393359,  3.83803844,  3.84202766,  3.84600878,
                        3.84998393,  3.85395193,  3.85802197,  3.86208749,  3.86604047,
                        3.86999369,  3.87394214,  3.87799811,  3.88194633,  3.88600349,
                        3.88995481,  3.89401698,  3.89797616,  3.90193915,  3.90601683,
                        3.90999269,  3.91408467,  3.91796803,  3.92196584,  3.92597222,
                        3.92998838,  3.93401074,  3.93804169,  3.94197202,  3.9459095,
                        3.95007277,  3.95402312,  3.95797944,  3.96194077,  3.96590614], dtype='float32')

VIIRS_RSR['I04']['det-1']['wavelength'] = I4_WAVELENGTH
VIIRS_RSR['I04']['det-1']['response'] = I4_RESPONSE
VIIRS_RSR['I04']['det-1']['central_wavelength'] = 3.7460763637226693

VIIRS_RSR['M12'] = {}
VIIRS_RSR['M12']['det-1'] = {}
M12_WAVELENGTH = np.array([3.50669217,  3.51322079,  3.51976728,  3.52643943,  3.53301215,
                           3.53959203,  3.546175,  3.55287051,  3.55944896,  3.56601906,
                           3.57257748,  3.57923317,  3.58575845,  3.59237552,  3.59907913,
                           3.60554028,  3.61219764,  3.6188333,  3.62544608,  3.63204026,
                           3.63861847,  3.64518261,  3.65184593,  3.65839601,  3.6649456,
                           3.67160821,  3.67827654,  3.68485141,  3.69144225,  3.69805193,
                           3.7045753,  3.71122766,  3.71779394,  3.72449064,  3.73098779,
                           3.73761344,  3.74425411,  3.75079513,  3.75745511,  3.76400733,
                           3.77067137,  3.77721882,  3.78386998,  3.79039693,  3.79702044,
                           3.80362248,  3.81020689,  3.81687641,  3.82341433,  3.8300364,
                           3.83652687,  3.84321165,  3.84976912,  3.85630941,  3.86294222], dtype='float32')
M12_RESPONSE = np.array([0.0064421,  0.0084001,  0.0109988,  0.0143879,  0.0197545,
                         0.0270981,  0.0370352,  0.0512599,  0.0715467,  0.0987869,
                         0.1393604,  0.195684,  0.26579589,  0.36917099,  0.509821,
                         0.63852757,  0.74241519,  0.82375473,  0.87010688,  0.89455551,
                         0.91357207,  0.92787379,  0.95018548,  0.97198248,  0.98594999,
                         0.99682951,  1.,  0.99573219,  0.98468697,  0.98146093,
                         0.97062051,  0.95142138,  0.927858,  0.9119851,  0.89879388,
                         0.89661211,  0.8987267,  0.89272481,  0.87440962,  0.83271909,
                         0.77336842,  0.69556081,  0.60315871,  0.49959281,  0.39389691,
                         0.302542,  0.2273816,  0.16862389,  0.1276994,  0.0968111,
                         0.0743906,  0.0573153,  0.0445903,  0.0345158,  0.0268065], dtype='float32')

VIIRS_RSR['M12']['det-1']['wavelength'] = M12_WAVELENGTH
VIIRS_RSR['M12']['det-1']['response'] = M12_RESPONSE
VIIRS_RSR['M12']['det-1']['central_wavelength'] = 3.6954317366170288


class RSRTestDataModis(object):
    """RSR test data for Aqua Modis."""

    def __init__(self):
        """Make the test data set of relative spectral responses."""
        self.rsr = TEST_RSR


class TestSeviriConversions(unittest.TestCase):
    """Testing the conversions between radiances and brightness temperatures."""

    def setUp(self):
        """Set up."""
        with patch('pyspectral.radiance_tb_conversion.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = SEV_RSR
            instance.unit = 'cm-1'
            instance.si_scale = 100.

            self.sev1 = RadTbConverter('Meteosat-9', 'seviri', 'IR3.9',
                                       wavespace='wavenumber')

        self.sev2 = SeviriRadTbConverter('Meteosat-9', 'IR3.9')

    def test_rad2tb(self):
        """Unit testing the radiance to brightness temperature conversion."""
        res = self.sev1.tb2radiance(TEST_TBS, lut=False)
        self.assertTrue(np.allclose(TRUE_RADS_SEVIRI, res['radiance']))

    def test_conversion_simple(self):
        """Test the conversion based on the non-linear approximation (SEVIRI).

        Test the tb2radiance function to convert radiances to Tb's
        using tabulated coefficients based on a non-linear approximation

        """
        retv = self.sev2.tb2radiance(TEST_TBS)
        rads = retv['radiance']
        # Units space = wavenumber (cm-1):
        tbs = self.sev2.radiance2tb(rads)
        self.assertTrue(np.allclose(TEST_TBS, tbs))

        np.random.seed()
        tbs1 = 200.0 + np.random.random(50) * 150.0
        retv = self.sev2.tb2radiance(tbs1)
        rads = retv['radiance']
        tbs = self.sev2.radiance2tb(rads)
        self.assertTrue(np.allclose(tbs1, tbs))

    def test_conversions_methods(self):
        """Test the conversion methods.

        Using the two diferent conversion methods to verify that they give
        approximately the same results. Conversion from Tb's to Radiances
        only.

        """
        # Units space = wavenumber (cm-1):
        retv2 = self.sev2.tb2radiance(TEST_TBS)
        retv1 = self.sev1.tb2radiance(TEST_TBS)

        rads1 = retv1['radiance']
        rads2 = retv2['radiance']
        self.assertTrue(np.allclose(rads1, rads2))

    def tearDown(self):
        """Clean up."""
        pass


class TestRadTbConversions(unittest.TestCase):
    """Testing the conversions between radiances and brightness temperatures."""

    def setUp(self):
        """Set up."""
        # mymock:
        with patch('pyspectral.radiance_tb_conversion.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = TEST_RSR
            instance.unit = '1e-6 m'
            instance.si_scale = 1e-6

            self.modis = RadTbConverter('EOS-Aqua', 'modis', '20')
            self.modis2 = RadTbConverter('EOS-Aqua', 'modis', 3.75)

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse.load')
    @patch('pyspectral.rsr_reader.download_rsr')
    def test_get_bandname(self, download_rsr, load, isfile, exists):
        """Test getting the band name from the wave length."""
        load.return_code = None
        download_rsr.return_code = None
        isfile.return_code = True
        exists.return_code = True

        with patch('pyspectral.radiance_tb_conversion.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = VIIRS_RSR
            instance.unit = 'm'
            instance.si_scale = 1.

            with self.assertRaises(AttributeError):
                RadTbConverter('Suomi-NPP', 'viirs', 3.7)

    def test_rad2tb(self):
        """Unit testing the radiance to brightness temperature conversion."""
        res = self.modis.tb2radiance(TEST_TBS, lut=False)
        self.assertTrue(np.allclose(TRUE_RADS, res['radiance']))

        res = self.modis2.tb2radiance(TEST_TBS, lut=False)
        self.assertTrue(np.allclose(TRUE_RADS, res['radiance']))

        rad = res['radiance']
        tbs = self.modis.radiance2tb(rad)
        self.assertTrue(np.allclose(TEST_TBS, tbs, atol=0.25))

        res = self.modis.tb2radiance(TEST_TBS, lut=False, normalized=False)
        integral = self.modis.rsr_integral
        self.assertTrue(np.allclose(TRUE_RADS * integral, res['radiance']))

        res = self.modis.tb2radiance(237., lut=False)
        self.assertAlmostEqual(16570.579551068, res['radiance'])

        res = self.modis.tb2radiance(277., lut=False)
        self.assertAlmostEqual(167544.39368663222, res['radiance'])

        res = self.modis.tb2radiance(1.1, lut=False)
        self.assertAlmostEqual(0.0, res['radiance'])

        res = self.modis.tb2radiance(11.1, lut=False)
        self.assertAlmostEqual(0.0, res['radiance'])

        res = self.modis.tb2radiance(100.1, lut=False)
        self.assertAlmostEqual(5.3940515573e-06, res['radiance'])

        res = self.modis.tb2radiance(200.1, lut=False)
        self.assertAlmostEqual(865.09759706, res['radiance'])

    def tearDown(self):
        """Clean up."""
        pass
