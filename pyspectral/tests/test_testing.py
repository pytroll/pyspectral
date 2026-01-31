"""Tests for the testing utilities in pyspectral.testing."""

import numpy as np
import pytest

from pyspectral.testing import mock_rayleigh, mock_rsr, mock_tb_conversion


@pytest.mark.parametrize("use_tmp_path", [False, True])
def test_tb_conversion(tmp_path, use_tmp_path):
    """Test basic Calculator mocking and path being provided or not."""
    from pyspectral.near_infrared_reflectance import Calculator

    tp = tmp_path if use_tmp_path else None
    with mock_tb_conversion(tb2rad_dir=tp, central_wavelengths={"20": 3.75}):
        refl37 = Calculator("EOS-Aqua", "modis", "20")
        expected = 2.001793e-08  # unit = "m" (meter)
        np.testing.assert_allclose(refl37.rsr_integral, expected)


@pytest.mark.parametrize("use_tmp_path", [False, True])
def test_rsr(tmp_path, use_tmp_path):
    """Test basic RSR mocking and path being provided or not."""
    from pyspectral.rsr_reader import RelativeSpectralResponse

    tp = tmp_path if use_tmp_path else None
    with mock_rsr(rsr_dir=tp):
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        test_rsr.convert()


@pytest.mark.parametrize("use_tmp_path", [False, True])
def test_rayleigh(tmp_path, use_tmp_path):
    """Test basic Rayleigh mocking and path being provided or not."""
    from pyspectral.rayleigh import Rayleigh

    tp = tmp_path if use_tmp_path else None
    dtype = np.float32
    sun_zenith = np.array([67.0, 32.0], dtype=dtype)
    sat_zenith = np.array([45.0, 18.0], dtype=dtype)
    azidiff = np.array([150.0, 110.0], dtype=dtype)
    redband_refl = np.array([14.0, 5.0], dtype=dtype)
    with mock_rayleigh(rayleigh_dir=tp):
        rayl = Rayleigh("NOAA-20", "VIIRS", atmosphere="midlatitude summer")
        rayl.get_reflectance(sun_zenith, sat_zenith, azidiff, "I01", redband_refl)
