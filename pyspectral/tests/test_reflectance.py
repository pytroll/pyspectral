"""Unit testing the 3.7 micron reflectance calculations."""

from unittest.mock import patch

import numpy as np
import pytest

from pyspectral.near_infrared_reflectance import TERMINATOR_LIMIT, Calculator, get_as_array
from pyspectral.testing import mock_tb_conversion

TEST_RSR = {'20': {},
            '99': {}}
TEST_RSR['20']['det-1'] = {}
TEST_RSR['20']['det-1']['central_wavelength'] = 3.780281935
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

TEST_RSR['99']['det-1'] = {}
TEST_RSR['99']['det-1']['central_wavelength'] = 10.8
TEST_RSR['99']['det-1']['wavelength'] = np.array([
    10.6123999,
    10.7563652,
    10.8563975,
    10.9064275,
    10.9535347], dtype='double')

TEST_RSR['99']['det-1']['response'] = np.array([
    0.33792,
    0.86008,
    1.,
    0.67429,
    0.07141], dtype='double')

TEST_RSR_WN = {'20': {}}
TEST_RSR_WN['20']['det-1'] = {}
WVN = np.array([2529.38208008, 2533.8840332, 2540.390625, 2546.81494141,
                2553.30883789, 2559.88354492, 2566.40722656, 2573.02270508,
                2579.72949219, 2586.37451172, 2593.09375, 2599.87548828,
                2606.55371094, 2613.41674805, 2620.29760742, 2627.18286133,
                2634.06005859, 2641.07421875, 2648.06713867, 2655.03930664,
                2662.14794922, 2669.25170898, 2676.36572266, 2683.50805664,
                2690.69702148, 2697.95288086, 2705.29199219, 2712.56982422,
                2719.94970703, 2727.43554688, 2734.8605957, 2742.38012695,
                2749.9831543, 2757.48510742, 2765.21142578, 2768.24291992],
               dtype='float32')
RESP = np.array([0.01, 0.01414, 0.02085, 0.02925, 0.04151,
                 0.07141, 0.14851999, 0.27761999, 0.44714999, 0.67429,
                 0.92676002, 1., 0.94808, 0.94718999, 0.94256002,
                 0.91057998, 0.91036999, 0.95687002, 0.95410001, 0.88922,
                 0.85412002, 0.87696999, 0.86610001, 0.86008, 0.92855,
                 0.96077001, 0.81814998, 0.59105998, 0.33792001, 0.16644999,
                 0.0849, 0.05028, 0.03226, 0.01987, 0.0118,
                 0.01], dtype='float32')

TEST_RSR_WN['20']['det-1']['central_wavelength'] = 3.780281935
TEST_RSR_WN['20']['det-1']['wavenumber'] = WVN
TEST_RSR_WN['20']['det-1']['response'] = RESP


class TestReflectance:
    """Unit testing the reflectance calculations."""

    def test_rsr_integral(self, tmp_path):
        """Test calculating the integral of the relative spectral response function."""
        return_value = {
            "description": "ABCD",
            "instrument": "modis",
            "platform_name": "EOS-Aqua",
            "band_names": list(TEST_RSR.keys()),
            "rsr": TEST_RSR,
        }
        with mock_tb_conversion(tb2rad_dir=tmp_path, return_value=return_value):
            refl37 = Calculator('EOS-Aqua', 'modis', '20')

        expected = 1.8563451e-07  # unit = 'm' (meter)
        np.testing.assert_allclose(refl37.rsr_integral, expected)

    def test_rsr_integral_wavenumber(self, tmp_path):
        """Test calculating the integral of the relative spectral response function in wavenumber."""
        return_value = {
            "description": "ABCD",
            "instrument": "modis",
            "platform_name": "EOS-Aqua",
            "band_names": list(TEST_RSR_WN.keys()),
            "rsr": TEST_RSR_WN,
        }

        with mock_tb_conversion(tb2rad_dir=tmp_path, return_value=return_value):
            refl37 = Calculator('EOS-Aqua', 'modis', '20', wavespace='wavenumber')

        expected = 13000.385  # SI units = 'm-1' (1/meter)
        res = refl37.rsr_integral
        np.testing.assert_allclose(res / expected, 1.0, 6)

    def test_reflectance_invalid_channel(self, tmp_path):
        """Test requesting non-existent channel causes an error."""
        return_value = {
            "description": "ABCD",
            "instrument": "viirs",
            "platform_name": "Suomi-NPP",
            "band_names": ["ch20", "99"],
            "rsr": TEST_RSR,
        }
        with mock_tb_conversion(tb2rad_dir=tmp_path, return_value=return_value):
            # VIIRS doesn't have a channel '20' like MODIS so the generic
            # mapping this test will end up using will find 'ch20' for VIIRS
            with pytest.raises(NotImplementedError):
                Calculator('Suomi-NPP', 'viirs', 10.8)

    def test_reflectance_viirs(self, tmp_path):
        """Test the derivation of the reflective part of a 3.7 micron band."""
        viirs_rsr = {"ch20": TEST_RSR["20"], "99": TEST_RSR["99"]}
        return_value = {
            "description": "ABCD",
            "instrument": "viirs",
            "platform_name": "Suomi-NPP",
            "band_names": list(viirs_rsr.keys()),
            "rsr": viirs_rsr,
        }
        with mock_tb_conversion(tb2rad_dir=tmp_path, return_value=return_value):
            refl37 = Calculator('Suomi-NPP', 'viirs', 3.7)
            assert refl37.bandwavelength == 3.7
            assert refl37.bandname == 'ch20'
            # Default sunz-threshold used to stay on day side and away from terminator:
            assert refl37.sunz_threshold == 85.0

    def test_reflectance_custom_limits(self, tmp_path):
        """Test get_reflectance with custom sunz threshold and masking limits."""
        return_value = {
            "description": "ABCD",
            "instrument": "modis",
            "platform_name": "EOS-Aqua",
            "band_names": list(TEST_RSR.keys()),
            "rsr": TEST_RSR,
        }
        with mock_tb_conversion(tb2rad_dir=tmp_path, return_value=return_value):
            refl37_sz88 = Calculator('EOS-Aqua', 'modis', '20', sunz_threshold=88.0, masking_limit=None)
            assert refl37_sz88.sunz_threshold == 88.0
            assert refl37_sz88.masking_limit is None
            assert refl37_sz88.bandwavelength == pytest.approx(3.780282, abs=1e-5)
            assert refl37_sz88.bandname == '20'

        sunz = np.array([85.1])
        tb3 = 290.
        tb4 = 282.
        refl_sz88 = refl37_sz88.reflectance_from_tbs(sunz, tb3, tb4)
        np.testing.assert_allclose(refl_sz88[0], 1.2064644, 6)

    def test_reflectance_default_limits(self, tmp_path):
        """Test get_reflectance with default sunz threshold and masking limits."""
        return_value = {
            "description": "ABCD",
            "instrument": "modis",
            "platform_name": "EOS-Aqua",
            "band_names": list(TEST_RSR.keys()),
            "rsr": TEST_RSR,
        }
        with mock_tb_conversion(tb2rad_dir=tmp_path, return_value=return_value):
            refl37 = Calculator('EOS-Aqua', 'modis', '20')
            assert refl37.sunz_threshold == TERMINATOR_LIMIT
            assert refl37.masking_limit == TERMINATOR_LIMIT

        sunz = 80.
        tb3 = 290.
        tb4 = 282.
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        np.testing.assert_allclose(refl[0], 0.251245010648, 6)

        sunz = 85.
        tb3 = 290.
        tb4 = 282.
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        np.testing.assert_allclose(refl[0], 1.12236884, 6)

        sunz = np.array([85.1])
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        assert np.isnan(refl[0])

        tb3x = refl37.emissive_part_3x()
        np.testing.assert_allclose(tb3x, 276.213054, 6)

        sunz = np.array([80.])
        tb3 = np.array([295.])
        tb4 = np.array([282.])
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        np.testing.assert_allclose(refl[0], 0.452497961, 6)

        tb3x = refl37.emissive_part_3x()
        np.testing.assert_allclose(tb3x, 270.077268, 6)

        sunz = np.array([50.])
        tb3 = np.array([300.])
        tb4 = np.array([285.])
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        np.testing.assert_allclose(refl[0], 0.1189217, 6)

        tb3x = refl37.emissive_part_3x()
        np.testing.assert_allclose(tb3x, 282.455426, 6)

        sunz = np.array([50.])
        tb3 = np.ma.masked_array([300.], mask=False)
        tb4 = np.ma.masked_array([285.], mask=False)
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        assert hasattr(refl, 'mask')

        sunz = np.array([80.], dtype=np.float32)
        tb3 = np.array([295.], dtype=np.float32)
        tb4 = np.array([282.], dtype=np.float32)
        refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
        np.testing.assert_allclose(refl, np.array([0.45249779], np.float32))
        assert refl.dtype == np.float32

        try:
            import dask.array as da
            import dask.config

            from pyspectral.tests.unittest_helpers import ComputeCountingScheduler

            with dask.config.set(scheduler=ComputeCountingScheduler(max_computes=0)):
                sunz = da.from_array([50.], chunks=10)
                tb3 = da.from_array([300.], chunks=10)
                tb4 = da.from_array([285.], chunks=10)
                refl = refl37.reflectance_from_tbs(sunz, tb3, tb4)
                assert hasattr(refl, 'compute')
        except ImportError:
            pass


def test_get_as_array_from_scalar_input_dask():
    """Test the function to return an array when input is a scalar - using Dask."""
    res = get_as_array(2.3)
    if hasattr(res, 'compute'):
        assert res.compute()[0] == 2.3
    else:
        assert res[0] == 2.3


def test_get_as_array_from_scalar_input_numpy():
    """Test the function to return an array when input is a scalar - using Numpy."""
    with patch('pyspectral.near_infrared_reflectance.asanyarray', new=np.asanyarray):
        res = get_as_array(2.3)

    assert res[0] == 2.3


def test_get_as_array_from_numpy_array_input_dask():
    """Test the function to return an array when input is a numpy array - using Dask."""
    res = get_as_array(np.array([1.0, 2.0]))
    if hasattr(res, 'compute'):
        np.testing.assert_allclose(res.compute(), np.array([1.0, 2.0]), 5)
    else:
        np.testing.assert_allclose(res, np.array([1.0, 2.0]), 5)


def test_get_as_array_from_numpy_array_input_numpy():
    """Test the function to return an array when input is a numpy array - using Numpy."""
    from pyspectral.near_infrared_reflectance import get_as_array

    with patch('pyspectral.near_infrared_reflectance.asanyarray', new=np.asanyarray):
        res = get_as_array(np.array([1.0, 2.0]))

    np.testing.assert_allclose(res, np.array([1.0, 2.0]), 5)


def test_get_as_array_from_list_input_dask():
    """Test the function to return an array when input is a list - using Dask."""
    res = get_as_array([1.0, 2.0])
    if hasattr(res, 'compute'):
        np.testing.assert_allclose(res.compute(), np.array([1.0, 2.0]), 5)
    else:
        np.testing.assert_allclose(res, np.array([1.0, 2.0]), 5)


def test_get_as_array_from_list_input_numpy():
    """Test the function to return an array when input is a list - using Numpy."""
    with patch('pyspectral.near_infrared_reflectance.asanyarray', new=np.asanyarray):
        res = get_as_array([1.1, 2.2])

    np.testing.assert_allclose(res, np.array([1.1, 2.2]), 5)
