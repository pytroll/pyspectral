#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2022 Pytroll developers
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Unittest for the rayleigh correction utilities."""
import contextlib
import os
import unittest
from unittest.mock import patch

import dask.array as da
import h5py
import numpy as np
import pytest

from pyspectral import rayleigh, utils
from pyspectral.tests.data import (
    TEST_RAYLEIGH_AZID_COORD,
    TEST_RAYLEIGH_LUT,
    TEST_RAYLEIGH_SATZ_COORD,
    TEST_RAYLEIGH_SUNZ_COORD,
    TEST_RAYLEIGH_WVL_COORD,
)
from pyspectral.utils import ATM_CORRECTION_LUT_VERSION

TEST_RAYLEIGH_RESULT1 = np.array([10.339923,    8.64748], dtype='float32')
TEST_RAYLEIGH_RESULT2 = np.array([9.653559, 8.464997], dtype='float32')
TEST_RAYLEIGH_RESULT3 = np.array([5.488735, 8.533125], dtype='float32')
TEST_RAYLEIGH_RESULT4 = np.array([0.0,    8.64748], dtype='float32')
TEST_RAYLEIGH_RESULT5 = np.array([9.653559, np.nan], dtype='float32')
TEST_RAYLEIGH_RESULT_R1 = np.array([16.66666667, 20.83333333, 25.], dtype='float32')
TEST_RAYLEIGH_RESULT_R2 = np.array([0., 6.25, 12.5], dtype='float32')

TEST_ZENITH_ANGLES_RESULTS = np.array([68.67631374, 68.67631374, 32., 0.])


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


@pytest.fixture
def fake_lut_hdf5(tmp_path):
    """Create a fake LUT HDF5 file and necessary mocks to use it."""
    aerosol_type = "marine_clean_aerosol"
    base_dir = tmp_path / aerosol_type
    base_dir.mkdir()
    _create_fake_lut_version_file(base_dir, aerosol_type)
    for atm_type in ("midlatitude_summer", "subarctic_winter", "tropical", "us-standard"):
        _create_fake_lut_hdf5_file(base_dir, atm_type)
    fake_config = {
        "rsr_dir": str(tmp_path),
        "rayleigh_dir": str(tmp_path),
        "download_from_internet": False,
    }
    with patch('pyspectral.rayleigh.get_config', lambda: fake_config), \
            patch('pyspectral.utils.get_config', lambda: fake_config):
        yield None


def _create_fake_lut_version_file(base_dir, aerosol_type):
    lut_version = ATM_CORRECTION_LUT_VERSION[aerosol_type]["version"]
    lutfiles_path = str(base_dir / ATM_CORRECTION_LUT_VERSION[aerosol_type]["filename"])
    with open(lutfiles_path, "w") as version_file:
        version_file.write(lut_version)


def _create_fake_lut_hdf5_file(base_dir, atm_type) -> str:
    filename = str(base_dir / f"rayleigh_lut_{atm_type}.h5")
    with h5py.File(filename, "w") as h5f:
        h5f["reflectance"] = TEST_RAYLEIGH_LUT
        h5f["wavelengths"] = TEST_RAYLEIGH_WVL_COORD
        h5f["azimuth_difference"] = TEST_RAYLEIGH_AZID_COORD
        h5f["sun_zenith_secant"] = TEST_RAYLEIGH_SUNZ_COORD
        h5f["satellite_zenith_secant"] = TEST_RAYLEIGH_SATZ_COORD
    return filename


def _create_rayleigh(platform='NOAA-20', sensor='VIIRS'):
    rayl = rayleigh.Rayleigh(platform, sensor, atmosphere='midlatitude summer')
    return rayl


@contextlib.contextmanager
def mocked_rsr():
    """Mock the RSR class used by the Rayleigh class with fake data."""
    with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
        instance = mymock.return_value
        instance.rsr = RelativeSpectralResponseTestData().rsr
        instance.unit = '1e-6 m'
        instance.si_scale = 1e-6
        yield mymock


def _create_dask_array(input_data, dtype):
    return da.from_array(np.array(input_data, dtype=dtype))


class TestRayleighDask:
    """Class for testing pyspectral.rayleigh - with dask-arrays as input."""

    def test_dask_clipping_angles_with_nans(self):
        """Test the clipping of angles outside coordinate range - with nan's in input."""
        from pyspectral.rayleigh import _clip_angles_inside_coordinate_range
        zenith_angle = da.array([79., 69., 32., np.nan])
        result = _clip_angles_inside_coordinate_range(zenith_angle, 2.75)
        np.testing.assert_allclose(result, TEST_ZENITH_ANGLES_RESULTS)

    def test_get_reflectance_dask_redband_outside_clip(self, fake_lut_hdf5):
        """Test getting the reflectance correction with dask inputs - using red band reflections outside 20-100."""
        sun_zenith = da.array([67., 32.])
        sat_zenith = da.array([45., 18.])
        azidiff = da.array([150., 110.])
        redband_refl = da.array([108., -0.5])
        viirs_rayl = _create_rayleigh()
        with mocked_rsr():
            refl_corr = viirs_rayl.get_reflectance(sun_zenith, sat_zenith, azidiff, 'ch3', redband_refl)
        np.testing.assert_allclose(refl_corr, TEST_RAYLEIGH_RESULT4)
        assert isinstance(refl_corr, da.Array)

    @pytest.mark.parametrize("dtype", [np.float32, np.float64])
    @pytest.mark.parametrize("use_dask", [False, True])
    @pytest.mark.parametrize(
        ("input_data", "exp_result"),
        [
            (([67.0, 32.0], [45.0, 18.0], [150.0, 110.0], [14.0, 5.0]), TEST_RAYLEIGH_RESULT1),
            (([60.0, 20.0], [49.0, 26.0], [140.0, 130.0], [12.0, 8.0]), TEST_RAYLEIGH_RESULT2),
        ]
    )
    def test_get_reflectance(self, fake_lut_hdf5, dtype, use_dask, input_data, exp_result):
        """Test getting the reflectance correction with dask inputs."""
        array_func = np.array if not use_dask else _create_dask_array
        sun_zenith = array_func(input_data[0], dtype=dtype)
        sat_zenith = array_func(input_data[1], dtype=dtype)
        azidiff = array_func(input_data[2], dtype=dtype)
        redband_refl = array_func(input_data[3], dtype=dtype)
        rayl = _create_rayleigh()
        with mocked_rsr():
            refl_corr = rayl.get_reflectance(sun_zenith, sat_zenith, azidiff, 'ch3', redband_refl)

        if use_dask:
            assert isinstance(refl_corr, da.Array)
            refl_corr_np = refl_corr.compute()
            assert refl_corr_np.dtype == refl_corr.dtype  # check that the final numpy array's dtype is equal
            refl_corr = refl_corr_np

        assert isinstance(refl_corr, np.ndarray)
        np.testing.assert_allclose(refl_corr, exp_result.astype(dtype), atol=4.0e-06)
        assert refl_corr.dtype == dtype  # check that the dask array's dtype is equal

    def test_get_reflectance_wvl_outside_range(self, fake_lut_hdf5):
        """Test getting the reflectance correction with wavelength outside correction range."""
        with mocked_rsr() as rsr_obj:
            rsr_obj.side_effect = IOError("No rsr data in pyspectral for this platform and sensor")
            sun_zenith = da.from_array([50., 10.])
            sat_zenith = da.from_array([39., 16.])
            azidiff = da.from_array([170., 110.])
            redband_refl = da.from_array([29., 12.])
            rayl = rayleigh.Rayleigh('UFO', 'unknown', atmosphere='midlatitude summer')

            # we gave a direct wavelength so the RSR object shouldn't be needed
            refl_corr = rayl.get_reflectance(sun_zenith, sat_zenith, azidiff, 1.2, redband_refl)
            np.testing.assert_allclose(refl_corr, 0)
            assert isinstance(refl_corr, da.Array)
            rsr_obj.assert_not_called()


class TestRayleigh:
    """Class for testing pyspectral.rayleigh."""

    def test_get_effective_wavelength_and_band_name_with_floats(self, fake_lut_hdf5):
        """Test getting the effective wavelength."""
        this = rayleigh.Rayleigh('Himawari-8', 'ahi')
        # Only ch3 (~0.63) testdata implemented yet...
        ewl, band_name = this._get_effective_wavelength_and_band_name(0.65)
        np.testing.assert_allclose(ewl, 650)  # 635.6167)
        assert isinstance(band_name, str)

        this = rayleigh.Rayleigh('Himawari-8', 'ahi')
        ewl, band_name = this._get_effective_wavelength_and_band_name(0.7)
        assert ewl == 700.0
        assert isinstance(band_name, str)
        ewl, band_name = this._get_effective_wavelength_and_band_name(0.9)
        assert ewl == 900.0
        assert isinstance(band_name, str)
        ewl, band_name = this._get_effective_wavelength_and_band_name(0.455)
        assert ewl == 455.0
        assert isinstance(band_name, str)

    def test_rayleigh_init(self, fake_lut_hdf5):
        """Test creating the Rayleigh object."""
        with patch('pyspectral.rayleigh.RelativeSpectralResponse') as mymock:
            instance = mymock.return_value
            instance.rsr = RelativeSpectralResponseTestData().rsr

            with pytest.raises(AttributeError):
                rayleigh.Rayleigh('Himawari-8', 'ahi', atmosphere='unknown')

            with pytest.raises(AttributeError):
                rayleigh.Rayleigh('Himawari-8', 'ahi', aerosol_type='unknown')

            this = rayleigh.Rayleigh('Himawari-8', 'ahi', atmosphere='subarctic winter')
            assert os.path.basename(this.reflectance_lut_filename).endswith('subarctic_winter.h5')
            assert this.sensor == 'ahi'

            this = rayleigh.Rayleigh('NOAA-19', 'avhrr/3', atmosphere='tropical')
            assert this.sensor == 'avhrr3'

    def test_clipping_angles_with_nans(self):
        """Test the clipping of angles outside coordinate range - with nan's in input."""
        from pyspectral.rayleigh import _clip_angles_inside_coordinate_range
        zenith_angle = np.array([79., 69., 32., np.nan])
        result = _clip_angles_inside_coordinate_range(zenith_angle, 2.75)
        np.testing.assert_allclose(result, TEST_ZENITH_ANGLES_RESULTS)

    def test_rayleigh_reduction(self, fake_lut_hdf5):
        """Test the code that reduces Rayleigh correction for high zenith angles."""
        # Test the Rayleigh reduction code
        sun_zenith = np.array([70., 65., 60.])
        in_rayleigh = [50, 50, 50]
        # Test case where no reduction is done.
        retv = rayleigh.Rayleigh.reduce_rayleigh_highzenith(sun_zenith, in_rayleigh, 70., 90., 1)
        np.testing.assert_allclose(retv, in_rayleigh)
        # Test case where moderate reduction is performed.
        retv = rayleigh.Rayleigh.reduce_rayleigh_highzenith(sun_zenith, in_rayleigh, 30., 90., 1)
        np.testing.assert_allclose(retv, TEST_RAYLEIGH_RESULT_R1)
        # Test case where extreme reduction is performed.
        retv = rayleigh.Rayleigh.reduce_rayleigh_highzenith(sun_zenith, in_rayleigh, 30., 90., 1.5)
        np.testing.assert_allclose(retv, TEST_RAYLEIGH_RESULT_R2)

    def test_rayleigh_getname(self):
        """Test logic for Rayleigh instrument selection."""
        with pytest.raises(ValueError):
            _create_rayleigh(platform='FY-4B')

        rayl = _create_rayleigh(platform='FY-4A', sensor='agri')
        assert rayl.sensor == 'agri'

        rayl = _create_rayleigh(platform='FY-4B', sensor='agri')
        assert rayl.sensor == 'agri'

        rayl = _create_rayleigh(platform='FY-4B', sensor='ghi')
        assert rayl.sensor == 'ghi'

        with pytest.raises(ValueError):
            _create_rayleigh(platform='FY-4B', sensor='nosensor')

    @patch('pyspectral.rayleigh.da', None)
    def test_get_reflectance_redband_outside_clip(self, fake_lut_hdf5):
        """Test getting the reflectance correction - using red band reflections outside 20 to 100."""
        sun_zenith = np.array([67., 32.])
        sat_zenith = np.array([45., 18.])
        azidiff = np.array([150., 110.])
        redband_refl = np.array([100., 20.])
        rayl = _create_rayleigh()
        with mocked_rsr():
            refl_corr1 = rayl.get_reflectance(
                sun_zenith, sat_zenith, azidiff, 'ch3', redband_refl)

        np.testing.assert_allclose(refl_corr1, TEST_RAYLEIGH_RESULT4)

        rng = np.random.default_rng(12345)
        rints_low = rng.integers(low=-10, high=20, size=2).astype('float')
        rints_high = rng.integers(low=100, high=200, size=2).astype('float')

        redband_refl = np.array([rints_high[0], rints_low[0]])
        with mocked_rsr():
            refl_corr2 = rayl.get_reflectance(
                sun_zenith, sat_zenith, azidiff, 'ch3', redband_refl)

        redband_refl = np.array([rints_high[1], rints_low[1]])
        with mocked_rsr():
            refl_corr3 = rayl.get_reflectance(
                sun_zenith, sat_zenith, azidiff, 'ch3', redband_refl)

        assert isinstance(refl_corr1, np.ndarray)
        assert isinstance(refl_corr2, np.ndarray)
        np.testing.assert_allclose(refl_corr1, refl_corr2)
        np.testing.assert_allclose(refl_corr2, refl_corr3)

    @patch('pyspectral.rayleigh.da', None)
    @pytest.mark.parametrize(
        ("sun_zenith", "sat_zenith", "azidiff", "redband_refl", "exp_result"),
        [
            (np.array([67., 32.]), np.array([45., 18.]), np.array([150., 110.]), np.array([14., 5.]),
             TEST_RAYLEIGH_RESULT1),
            (np.array([60., 20.]), np.array([49., 26.]), np.array([140., 130.]), np.array([12., 8.]),
             TEST_RAYLEIGH_RESULT2),
            (np.array([60., 20.]), np.array([49., 26.]), np.array([140., 130.]), np.array([12., np.nan]),
             TEST_RAYLEIGH_RESULT5),
        ]
    )
    @pytest.mark.parametrize("dtype", [np.float32, np.float64])
    def test_get_reflectance(self, fake_lut_hdf5, sun_zenith, sat_zenith, azidiff, redband_refl, exp_result, dtype):
        """Test getting the reflectance correction."""
        rayl = _create_rayleigh()
        with mocked_rsr():
            refl_corr = rayl.get_reflectance(
                sun_zenith.astype(dtype),
                sat_zenith.astype(dtype),
                azidiff.astype(dtype),
                'ch3',
                redband_refl.astype(dtype))
        assert isinstance(refl_corr, np.ndarray)
        np.testing.assert_allclose(refl_corr, exp_result.astype(dtype), atol=4.0e-06)

    @patch('pyspectral.rayleigh.da', None)
    def test_get_reflectance_no_rsr(self, fake_lut_hdf5):
        """Test getting the reflectance correction, simulating that we have no RSR data."""
        with mocked_rsr() as rsr_obj:
            rsr_obj.side_effect = IOError("No rsr data in pyspectral for this platform and sensor")
            sun_zenith = np.array([50., 10.])
            sat_zenith = np.array([39., 16.])
            azidiff = np.array([170., 110.])
            redband_refl = np.array([29., 12.])
            ufo = rayleigh.Rayleigh('UFO', 'unknown', atmosphere='midlatitude summer')
            with pytest.raises(KeyError):
                ufo.get_reflectance(sun_zenith, sat_zenith, azidiff, 'ch3', redband_refl)

    @patch('pyspectral.rayleigh.da', None)
    def test_get_reflectance_float_wavelength(self, fake_lut_hdf5):
        """Test getting the reflectance correction."""
        with mocked_rsr() as rsr_obj:
            rsr_obj.side_effect = IOError("No rsr data in pyspectral for this platform and sensor")
            sun_zenith = np.array([50., 10.])
            sat_zenith = np.array([39., 16.])
            azidiff = np.array([170., 110.])
            redband_refl = np.array([29., 12.])
            # rayl = _create_rayleigh()
            rayl = rayleigh.Rayleigh('UFO', 'unknown', atmosphere='midlatitude summer')

            # we gave a direct wavelength so the RSR object shouldn't be needed
            refl_corr = rayl.get_reflectance(sun_zenith, sat_zenith, azidiff, 0.634, redband_refl)
            np.testing.assert_allclose(refl_corr, TEST_RAYLEIGH_RESULT3)
            assert isinstance(refl_corr, np.ndarray)
            rsr_obj.assert_not_called()

    @patch('pyspectral.rayleigh.da', None)
    def test_get_reflectance_wvl_outside_range(self, fake_lut_hdf5):
        """Test getting the reflectance correction with wavelength outside correction range."""
        with mocked_rsr() as rsr_obj:
            rsr_obj.side_effect = IOError("No rsr data in pyspectral for this platform and sensor")
            sun_zenith = np.array([50., 10.])
            sat_zenith = np.array([39., 16.])
            azidiff = np.array([170., 110.])
            redband_refl = np.array([29., 12.])
            rayl = rayleigh.Rayleigh('UFO', 'unknown', atmosphere='midlatitude summer')

            # we gave a direct wavelength so the RSR object shouldn't be needed
            refl_corr = rayl.get_reflectance(sun_zenith, sat_zenith, azidiff, 1.2, redband_refl)
            np.testing.assert_allclose(refl_corr, 0)
            assert isinstance(refl_corr, np.ndarray)
            rsr_obj.assert_not_called()

    def test_get_reflectance_no_lut(self, fake_lut_hdf5):
        """Test that missing a LUT causes an exception.."""
        # test LUT doesn't have a subartic_summer file
        with pytest.raises(IOError):
            rayleigh.Rayleigh('UFO', 'unknown', atmosphere='subarctic summer')


@pytest.mark.parametrize(
    ("version", "exp_download"),
    [
        (None, False),
        ("v0.0.0", True),
    ],
)
def test_check_and_download(tmp_path, version, exp_download):
    """Test that check_and_download only downloads when necessary."""
    from pyspectral.rayleigh import check_and_download
    with _fake_lut_dir(tmp_path, version), unittest.mock.patch("pyspectral.rayleigh.download_luts") as download:
        check_and_download()
        if exp_download:
            download.assert_called()
        else:
            download.assert_not_called()


@contextlib.contextmanager
def _fake_lut_dir(tmp_path, lut_version):
    with _fake_get_config(tmp_path):
        for aerosol_type in utils.AEROSOL_TYPES:
            atype_version_fn = utils.ATM_CORRECTION_LUT_VERSION[aerosol_type]["filename"]
            atype_version = utils.ATM_CORRECTION_LUT_VERSION[aerosol_type]["version"]
            atype_subdir = tmp_path / aerosol_type
            atype_subdir.mkdir()
            version_filename = str(atype_subdir / atype_version_fn)
            with open(version_filename, "w") as version_file:
                version_file.write(lut_version or atype_version)
        yield


@contextlib.contextmanager
def _fake_get_config(tmp_path):
    def _get_config():
        return {
            "rayleigh_dir": str(tmp_path),
            "rsr_dir": str(tmp_path),
            "download_from_internet": True,
        }
    with unittest.mock.patch("pyspectral.rayleigh.get_config") as get_config, \
            unittest.mock.patch("pyspectral.utils.get_config") as get_config2:
        get_config.side_effect = _get_config
        get_config2.side_effect = _get_config
        yield
