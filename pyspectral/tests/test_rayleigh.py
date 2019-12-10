#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, 2017, 2018, 2019 Adam.Dybbroe

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

"""Unittest for the rayleigh correction utilities."""

import os
import sys
import numpy as np
import dask.array as da
from pyspectral import rayleigh
from pyspectral.rayleigh import BandFrequencyOutOfRange
from pyspectral.tests.data import (
    TEST_RAYLEIGH_LUT,
    TEST_RAYLEIGH_AZID_COORD,
    TEST_RAYLEIGH_SUNZ_COORD,
    TEST_RAYLEIGH_SATZ_COORD,
    TEST_RAYLEIGH_WVL_COORD)
from pyspectral.utils import RSR_DATA_VERSION

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3,):
    from mock import patch
else:
    from unittest.mock import patch

TEST_RAYLEIGH_RESULT1 = np.array([10.40727436,   8.69775471], dtype='float32')
TEST_RAYLEIGH_RESULT2 = np.array([9.71695252,  8.51415601], dtype='float32')
TEST_RAYLEIGH_RESULT3 = np.array([5.61532271,  8.69267476], dtype='float32')


# Mock some modules, so we don't need them for tests.

# sys.modules['pyresample'] = MagicMock()


class RelativeSpectralResponseTestData(object):
    """Create the class instance to hold the RSR test data."""

    def __init__(self):
        """Make a test data set of relative spectral responses."""
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
    """Class for testing pyspectral.rayleigh."""

    def setUp(self):
        """Set up the test."""
        self.cwvl = 0.4440124
        self.rsr = RelativeSpectralResponseTestData()
        self._res1 = da.from_array(TEST_RAYLEIGH_RESULT1, chunks=2)
        self._res2 = da.from_array(TEST_RAYLEIGH_RESULT2, chunks=2)
        self._res3 = da.from_array(TEST_RAYLEIGH_RESULT3, chunks=2)

        # mymock:
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = RelativeSpectralResponseTestData().rsr
            instance.unit = '1e-6 m'
            instance.si_scale = 1e-6

            self.viirs_rayleigh = rayleigh.Rayleigh('NOAA-20', 'viirs', atmosphere='midlatitude summer')

    def test_get_effective_wavelength(self):
        """Test getting the effective wavelength."""
        # mymock:
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = RelativeSpectralResponseTestData().rsr

            this = rayleigh.Rayleigh('Himawari-8', 'ahi')
            with self.assertRaises(BandFrequencyOutOfRange):
                this.get_effective_wavelength(0.9)

            # Only ch3 (~0.63) testdata implemented yet...
            ewl = this.get_effective_wavelength(0.65)
            self.assertAlmostEqual(ewl, 0.6356167)

        # mymock:
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.side_effect = IOError(
                'Fake that there is no spectral response file...')

            this = rayleigh.Rayleigh('Himawari-8', 'ahi')
            ewl = this.get_effective_wavelength(0.7)
            self.assertEqual(ewl, 0.7)
            ewl = this.get_effective_wavelength(0.9)
            self.assertEqual(ewl, 0.9)
            ewl = this.get_effective_wavelength(0.455)
            self.assertEqual(ewl, 0.455)

    @patch('os.path.exists')
    @patch('pyspectral.utils.download_luts')
    def test_rayleigh_init(self, download_luts, exists):
        """Test creating the Rayleigh object."""
        download_luts.return_code = None
        exists.return_code = True

        # mymock:
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = RelativeSpectralResponseTestData().rsr

            with self.assertRaises(AttributeError):
                this = rayleigh.Rayleigh('Himawari-8', 'ahi', atmosphere='unknown')

            with self.assertRaises(AttributeError):
                this = rayleigh.Rayleigh('Himawari-8', 'ahi', aerosol_type='unknown')

            this = rayleigh.Rayleigh('Himawari-8', 'ahi', atmosphere='subarctic winter')
            self.assertTrue(os.path.basename(this.reflectance_lut_filename).endswith('subarctic_winter.h5'))
            self.assertTrue(this.sensor == 'ahi')

            this = rayleigh.Rayleigh('NOAA-19', 'avhrr/3', atmosphere='tropical')
            self.assertTrue(this.sensor == 'avhrr3')

    @patch('pyspectral.rayleigh.HAVE_DASK', False)
    @patch('os.path.exists')
    @patch('pyspectral.utils.download_luts')
    @patch('pyspectral.rayleigh.get_reflectance_lut')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse._get_rsr_data_version')
    @patch('pyspectral.rayleigh.Rayleigh.get_effective_wavelength')
    def test_get_reflectance(self, get_effective_wvl,
                             get_rsr_version, get_reflectance_lut, download_luts, exists):
        """Test getting the reflectance correction."""
        rayl = TEST_RAYLEIGH_LUT
        wvl_coord = TEST_RAYLEIGH_WVL_COORD
        azid_coord = TEST_RAYLEIGH_AZID_COORD
        sunz_sec_coord = TEST_RAYLEIGH_SUNZ_COORD
        satz_sec_coord = TEST_RAYLEIGH_SATZ_COORD

        get_reflectance_lut.return_value = (rayl, wvl_coord, azid_coord,
                                            satz_sec_coord, sunz_sec_coord)
        download_luts.return_code = None
        exists.return_code = True
        get_rsr_version.return_code = RSR_DATA_VERSION
        get_effective_wvl.return_value = self.cwvl

        sun_zenith = np.array([67., 32.])
        sat_zenith = np.array([45., 18.])
        azidiff = np.array([150., 110.])
        blueband = np.array([14., 5.])
        retv = self.viirs_rayleigh.get_reflectance(
            sun_zenith, sat_zenith, azidiff, 'M2', blueband)
        self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT1))

        sun_zenith = np.array([60., 20.])
        sat_zenith = np.array([49., 26.])
        azidiff = np.array([140., 130.])
        blueband = np.array([12., 8.])
        retv = self.viirs_rayleigh.get_reflectance(
            sun_zenith, sat_zenith, azidiff, 'M2', blueband)
        self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT2))

    @patch('os.path.exists')
    @patch('pyspectral.utils.download_luts')
    @patch('pyspectral.rayleigh.get_reflectance_lut')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse.'
           '_get_rsr_data_version')
    @patch('pyspectral.rayleigh.Rayleigh.get_effective_wavelength')
    def test_get_reflectance_dask(self, get_effective_wvl,
                                  get_rsr_version, get_reflectance_lut,
                                  download_luts, exists):
        """Test getting the reflectance correction with dask inputs."""
        rayl = da.from_array(TEST_RAYLEIGH_LUT, chunks=(10, 10, 10, 10))
        wvl_coord = da.from_array(TEST_RAYLEIGH_WVL_COORD,
                                  chunks=(100,)).persist()
        azid_coord = da.from_array(TEST_RAYLEIGH_AZID_COORD, chunks=(1000,))
        sunz_sec_coord = da.from_array(TEST_RAYLEIGH_SUNZ_COORD,
                                       chunks=(1000,))
        satz_sec_coord = da.from_array(TEST_RAYLEIGH_SATZ_COORD,
                                       chunks=(1000,))

        get_reflectance_lut.return_value = (rayl, wvl_coord, azid_coord,
                                            satz_sec_coord, sunz_sec_coord)
        download_luts.return_code = None
        exists.return_code = True
        get_rsr_version.return_code = RSR_DATA_VERSION
        get_effective_wvl.return_value = self.cwvl

        sun_zenith = da.from_array(np.array([67., 32.]), chunks=2)
        sat_zenith = da.from_array(np.array([45., 18.]), chunks=2)
        azidiff = da.from_array(np.array([150., 110.]), chunks=2)
        blueband = da.from_array(np.array([14., 5.]), chunks=2)
        retv = self.viirs_rayleigh.get_reflectance(sun_zenith, sat_zenith, azidiff, 'M2', blueband)
        self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT1))
        self.assertIsInstance(retv, da.Array)

        sun_zenith = da.from_array(np.array([60., 20.]), chunks=2)
        sat_zenith = da.from_array(np.array([49., 26.]), chunks=2)
        azidiff = da.from_array(np.array([140., 130.]), chunks=2)
        blueband = da.from_array(np.array([12., 8.]), chunks=2)
        retv = self.viirs_rayleigh.get_reflectance(sun_zenith, sat_zenith, azidiff, 'M2', blueband)
        self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT2))
        self.assertIsInstance(retv, da.Array)

    @patch('os.path.exists')
    @patch('pyspectral.utils.download_luts')
    @patch('pyspectral.rayleigh.get_reflectance_lut')
    @patch('pyspectral.rsr_reader.RelativeSpectralResponse.'
           '_get_rsr_data_version')
    @patch('pyspectral.rayleigh.Rayleigh.get_effective_wavelength')
    def test_get_reflectance_numpy_dask(self, get_effective_wvl,
                                        get_rsr_version, get_reflectance_lut,
                                        download_luts, exists):
        """Test getting the reflectance correction with dask inputs."""
        rayl = da.from_array(TEST_RAYLEIGH_LUT, chunks=(10, 10, 10, 10))
        wvl_coord = da.from_array(TEST_RAYLEIGH_WVL_COORD,
                                  chunks=(100,)).persist()
        azid_coord = da.from_array(TEST_RAYLEIGH_AZID_COORD, chunks=(1000,))
        sunz_sec_coord = da.from_array(TEST_RAYLEIGH_SUNZ_COORD,
                                       chunks=(1000,))
        satz_sec_coord = da.from_array(TEST_RAYLEIGH_SATZ_COORD,
                                       chunks=(1000,))

        get_reflectance_lut.return_value = (rayl, wvl_coord, azid_coord,
                                            satz_sec_coord, sunz_sec_coord)
        download_luts.return_code = None
        exists.return_code = True
        get_rsr_version.return_code = RSR_DATA_VERSION
        get_effective_wvl.return_value = self.cwvl

        sun_zenith = np.array([67., 32.])
        sat_zenith = np.array([45., 18.])
        azidiff = np.array([150., 110.])
        blueband = np.array([14., 5.])
        retv = self.viirs_rayleigh.get_reflectance(sun_zenith, sat_zenith, azidiff, 'M2', blueband)
        self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT1))
        self.assertIsInstance(retv, np.ndarray)

        sun_zenith = np.array([60., 20.])
        sat_zenith = np.array([49., 26.])
        azidiff = np.array([140., 130.])
        blueband = np.array([12., 8.])
        retv = self.viirs_rayleigh.get_reflectance(sun_zenith, sat_zenith, azidiff, 'M2', blueband)
        self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT2))
        self.assertIsInstance(retv, np.ndarray)

    @patch('pyspectral.rayleigh.HAVE_DASK', False)
    @patch('os.path.exists')
    @patch('pyspectral.utils.download_luts')
    @patch('pyspectral.rayleigh.get_reflectance_lut')
    def test_get_reflectance_no_rsr(self, get_reflectance_lut, download_luts, exists):
        """Test getting the reflectance correction, simulating that we have no RSR data."""
        rayl = TEST_RAYLEIGH_LUT
        wvl_coord = TEST_RAYLEIGH_WVL_COORD
        azid_coord = TEST_RAYLEIGH_AZID_COORD
        sunz_sec_coord = TEST_RAYLEIGH_SUNZ_COORD
        satz_sec_coord = TEST_RAYLEIGH_SATZ_COORD

        get_reflectance_lut.return_value = (rayl, wvl_coord, azid_coord,
                                            satz_sec_coord, sunz_sec_coord)
        download_luts.return_code = None
        exists.return_code = True

        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            mymock.side_effect = IOError("No rsr data in pyspectral for this platform and sensor")
            instance.rsr = None
            instance.unit = '1e-6 m'
            instance.si_scale = 1e-6
            sun_zenith = np.array([50., 10.])
            sat_zenith = np.array([39., 16.])
            azidiff = np.array([170., 110.])
            blueband = np.array([29., 12.])
            ufo = rayleigh.Rayleigh('UFO', 'unknown')

            retv = ufo.get_reflectance(sun_zenith, sat_zenith, azidiff, 0.441, blueband)
            self.assertTrue(np.allclose(retv, TEST_RAYLEIGH_RESULT3))
