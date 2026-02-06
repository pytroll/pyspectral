"""Unit testing the generic rsr hdf5 reader."""
from __future__ import annotations

import contextlib
import unittest

import numpy as np
import pytest

from pyspectral.rsr_reader import RelativeSpectralResponse, RSRDict
from pyspectral.testing import mock_rsr_files, override_config
from pyspectral.utils import RSR_DATA_VERSION, RSR_DATA_VERSION_FILENAME, WAVE_NUMBER

TEST_RSR = {'20': {}, }
TEST_RSR['20']['det-1'] = {}
TEST_RSR['20']['det-1']['central_wavelength'] = 3.75
TEST_RSR['20']['det-1']['wavelength'] = np.array([
    3.6123999, 3.6163599, 3.6264927, 3.6363862, 3.646468,
    3.6564937, 3.6664478, 3.6765388, 3.6865413, 3.6964585,
    3.7065142, 3.716509, 3.7264658, 3.7364102, 3.7463682,
    3.7563652, 3.7664226, 3.7763396, 3.7863384, 3.7964207,
    3.8063589, 3.8163606, 3.8264089, 3.8364836, 3.8463381,
    3.8563975, 3.8664163, 3.8763755, 3.8864797, 3.8964978,
    3.9064275, 3.9164873, 3.9264729, 3.9364026, 3.9465107,
    3.9535347], dtype='float32')

TEST_RSR['20']['det-1']['response'] = np.array([
    0.01, 0.0118, 0.01987, 0.03226, 0.05028, 0.0849,
    0.16645, 0.33792, 0.59106, 0.81815, 0.96077, 0.92855,
    0.86008, 0.8661, 0.87697, 0.85412, 0.88922, 0.9541,
    0.95687, 0.91037, 0.91058, 0.94256, 0.94719, 0.94808,
    1., 0.92676, 0.67429, 0.44715, 0.27762, 0.14852,
    0.07141, 0.04151, 0.02925, 0.02085, 0.01414, 0.01], dtype='float32')

TEST_RSR2 = {'20': {}, }
TEST_RSR2['20']['det-1'] = {}
TEST_RSR2['20']['det-1']['central_wavelength'] = 3.75
TEST_RSR2['20']['det-1']['wavelength'] = TEST_RSR['20']['det-1']['wavelength'].copy()
TEST_RSR2['20']['det-1']['response'] = TEST_RSR['20']['det-1']['response'].copy()

RESULT_WVN_RSR = np.array([2529.38232422,  2533.8840332,  2540.390625,  2546.81494141,
                           2553.30859375,  2559.88378906,  2566.40722656,  2573.02270508,
                           2579.72949219,  2586.37451172,  2593.09375,  2599.87548828,
                           2606.55371094,  2613.41674805,  2620.29760742,  2627.18286133,
                           2634.06005859,  2641.07421875,  2648.06713867,  2655.03930664,
                           2662.14794922,  2669.25170898,  2676.36572266,  2683.50805664,
                           2690.69702148,  2697.95288086,  2705.29199219,  2712.56982422,
                           2719.94970703,  2727.43554688,  2734.8605957,  2742.37988281,
                           2749.9831543,  2757.48510742,  2765.21142578,  2768.24291992], dtype=np.float32)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"platform_name": "GOES-16"},
        {"instrument": "ABI"},
        {"filename": "/path/to/something", "instrument": "ABI"},
    ]
)
def test_get_rsr_invalid_args(kwargs):
    """Test invalid argument combinations cause errors."""
    with pytest.raises(ValueError):
        RelativeSpectralResponse(**kwargs)


def test_convert(tmp_path):
    """Test the conversion method."""
    return_value = {
        "description": "",
        "instrument": "modis",
        "platform_name": "EOS-Aqua",
        "band_names": list(TEST_RSR.keys()),
        "rsr": TEST_RSR,
    }
    with mock_rsr_files(tmp_path, return_value=return_value):
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        test_rsr.convert()
        np.testing.assert_allclose(test_rsr.rsr["20"]["det-1"]["central_wavenumber"], 2647.397, atol=1e-3)
        np.testing.assert_allclose(test_rsr.rsr["20"]["det-1"][WAVE_NUMBER], RESULT_WVN_RSR, 5)
        assert test_rsr._wavespace == WAVE_NUMBER

        with pytest.raises(NotImplementedError):
            test_rsr.convert()


def test_integral(tmp_path):
    """Test the calculation of the integral of the spectral responses."""
    return_value = {
        "description": "",
        "instrument": "modis",
        "platform_name": "EOS-Aqua",
        "band_names": list(TEST_RSR2.keys()),
        "rsr": TEST_RSR,
    }
    with mock_rsr_files(tmp_path, return_value=return_value):
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        test_rsr.rsr = TEST_RSR2
        res = test_rsr.integral("20")
        np.testing.assert_almost_equal(res["det-1"], 0.185634, 6)


def test_metadata_from_hdf5_with_platform_instrument(tmp_path):
    """Test metadata is accepted from HDF5 file."""
    return_value = {
        "description": "ABCD",
        "instrument": "modis123",
        "platform_name": "EOS-Aqua456",
        "band_names": list(TEST_RSR2.keys()),
        "rsr": TEST_RSR,
    }
    with mock_rsr_files(tmp_path, return_value=return_value):
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        assert test_rsr.description == "ABCD"
        # platform and instrument are not overwritten by file content
        assert test_rsr.platform_name == "EOS-Aqua"
        assert test_rsr.instrument == "modis"
        assert test_rsr.band_names == list(TEST_RSR2.keys())
        assert test_rsr.filename.name == "rsr_modis_EOS-Aqua.h5"


def test_get_band_from_wavelength(tmp_path):
    """Test metadata is accepted from HDF5 file."""
    return_value = {
        "description": "ABCD",
        "instrument": "modis123",
        "platform_name": "EOS-Aqua456",
        "band_names": list(TEST_RSR2.keys()),
        "rsr": TEST_RSR,
    }
    with mock_rsr_files(tmp_path, return_value=return_value):
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        assert test_rsr.get_bandname_from_wavelength(3.75) == "20"


def test_metadata_from_hdf5_with_filename(tmp_path):
    """Test metadata is accepted from HDF5 file when using a filename directly."""
    import h5py

    filename = tmp_path / "my_file.h5"
    band_names = ["ch1", "ch2", "ch3"]
    band_central_wvl = [0.47, 0.64, 0.865]
    response = np.linspace(0.0009, 1.0, 1000, dtype=np.float32)
    wvl = np.linspace(-0.04, 0.04, 1000, dtype=np.float32)
    with h5py.File(filename, "w") as h:
        h.attrs["band_names"] = band_names
        h.attrs["description"] = "ABCD"
        h.attrs["platform_name"] = "GOES-16"

        for band_name, band_cwl in zip(band_names, band_central_wvl):
            band_group = h.create_group(band_name)
            band_group.attrs["central_wavelength"] = band_cwl
            band_group.create_dataset("response", data=response)
            wvl_ds = band_group.create_dataset("wavelength", data=wvl + band_cwl)
            wvl_ds.attrs["scale"] = 1e-6
            wvl_ds.attrs["unit"] = "m"

    test_rsr = RelativeSpectralResponse(filename=filename)
    assert test_rsr.description == "ABCD"
    assert test_rsr.platform_name == "GOES-16"
    assert test_rsr.instrument == "abi"  # guessed from platform_name in file
    assert test_rsr.band_names == band_names
    assert test_rsr.filename == filename
    for band_name, band_cwl in zip(band_names, band_central_wvl):
        assert test_rsr.rsr[band_name]["det-1"]["central_wavelength"] == band_cwl
        # scaling and unscaling causes small differences in wavelength to not be *exactly* equal
        np.testing.assert_almost_equal(test_rsr.rsr[band_name]["det-1"]["wavelength"], (wvl + band_cwl))
        np.testing.assert_equal(test_rsr.rsr[band_name]["det-1"]["response"], response)


def test_platform_missing_sat_number(tmp_path):
    """Test missing 'sat_number' with 'platform' attribute in RSR file."""
    import h5py

    filename = tmp_path / "my_file.h5"
    band_names = ["1"]
    band_central_wvl = [0.47]
    response = np.linspace(0.0009, 1.0, 1000, dtype=np.float32)
    wvl = np.linspace(-0.04, 0.04, 1000, dtype=np.float32)
    with h5py.File(filename, "w") as h:
        h.attrs["band_names"] = band_names
        h.attrs["description"] = "ABCD"
        h.attrs["platform"] = "eos"

        for band_name, band_cwl in zip(band_names, band_central_wvl):
            band_group = h.create_group(band_name)
            band_group.attrs["central_wavelength"] = band_cwl
            band_group.create_dataset("response", data=response)
            wvl_ds = band_group.create_dataset("wavelength", data=wvl + band_cwl)
            wvl_ds.attrs["scale"] = 1e-6
            wvl_ds.attrs["unit"] = "m"

    test_rsr = RelativeSpectralResponse(filename=filename)
    assert test_rsr.platform_name is None


def test_metadata_via_sat_number(tmp_path):
    """Test an RSR file that uses 'platform' and 'sat_number'."""
    import h5py

    filename = tmp_path / "my_file.h5"
    band_names = ["1"]
    band_central_wvl = [0.47]
    response = np.linspace(0.0009, 1.0, 1000, dtype=np.float32)
    wvl = np.linspace(-0.04, 0.04, 1000, dtype=np.float32)
    with h5py.File(filename, "w") as h:
        h.attrs["band_names"] = band_names
        h.attrs["description"] = "ABCD"
        h.attrs["platform"] = "eos"
        h.attrs["sat_number"] = 2

        for band_name, band_cwl in zip(band_names, band_central_wvl):
            band_group = h.create_group(band_name)
            band_group.attrs["central_wavelength"] = band_cwl
            band_group.create_dataset("response", data=response)
            wvl_ds = band_group.create_dataset("wavelength", data=wvl + band_cwl)
            wvl_ds.attrs["scale"] = 1e-6
            wvl_ds.attrs["unit"] = "m"

    test_rsr = RelativeSpectralResponse(filename=filename)
    assert test_rsr.platform_name == "EOS-Aqua"
    assert test_rsr.instrument == "modis"


@pytest.mark.parametrize(
    ("band_name", "exp_value"),
    [
        ("M1", 0),
        ("M01", 0),
        ("VIS006", 1),
    ]
)
def test_rsr_dict(band_name, exp_value):
    """Test finding correct band names from utils dicts."""
    test_rsr = RSRDict(instrument="viirs")
    test_rsr["M1"] = 0
    test_rsr["VIS0.6"] = 1
    assert test_rsr[band_name] == exp_value


def test_rsr_dict_incorrect_band_alias():
    """Check exception raised if incorrect band name given."""
    test_rsr = RSRDict(instrument='viirs')

    with pytest.raises(KeyError):
        _ = test_rsr['VIS030']


def test_rsr_unconfigured_sensor():
    """Test RSRDict finds generic band conversions when specific sensor is not configured."""
    test_rsr = RSRDict(instrument="i dont exist")
    test_rsr["ch1"] = 2
    assert test_rsr['1'] == 2


@pytest.mark.parametrize(
    ("platform_name", "instrument", "exp_filename", "exp_instrument"),
    [
        ('FY-3D', 'mersi-2', 'rsr_mersi2_FY-3D.h5', 'mersi2'),
        ('TIROS-N', 'avhrr-1', 'rsr_avhrr1_TIROS-N.h5', 'avhrr1'),
        ('NOAA-12', 'avhrr-2', 'rsr_avhrr2_NOAA-12.h5', 'avhrr2'),
        ('NOAA-12', 'avhrr/2', 'rsr_avhrr2_NOAA-12.h5', 'avhrr2'),
        ('NOAA-19', 'avhrr/3', 'rsr_avhrr3_NOAA-19.h5', 'avhrr3'),
        ('GOES-16', 'abi', 'rsr_abi_GOES-16.h5', 'abi'),
        ('GOES-16', 'ABI', 'rsr_abi_GOES-16.h5', 'abi'),
        ('GOES-18', 'AbI', 'rsr_abi_GOES-18.h5', 'abi'),
    ]
)
def test_get_rsr_from_platform_and_instrument(tmp_path, platform_name, instrument, exp_filename, exp_instrument):
    """Test getting the rsr filename correct when specifying the platform and instrument names."""
    with mock_rsr_files(tmp_path):
        test_rsr = RelativeSpectralResponse(platform_name, instrument)
        assert test_rsr.platform_name == platform_name
        assert test_rsr.instrument == exp_instrument
        assert test_rsr.filename.name == exp_filename


def test_rsr_download_from_platform_and_instrument(tmp_path):
    """Test that RSR files are downloaded when not present or not up to date."""
    with (mock_rsr_files(tmp_path, rsr_data_version="v0.0.0"),
          unittest.mock.patch("pyspectral.rsr_reader.download_rsr") as download):
        RelativeSpectralResponse("GOES-16", "abi")
        download.assert_called()


@pytest.mark.parametrize(
    ("version", "exp_download"),
    [
        (RSR_DATA_VERSION, False),
        ("v1.0.0", True),
        (None, True),
    ],
)
def test_check_and_download(tmp_path, version, exp_download):
    """Test that check_and_download only downloads when necessary."""
    from pyspectral.rsr_reader import check_and_download
    with _fake_rsr_dir(tmp_path, version), unittest.mock.patch("pyspectral.rsr_reader.download_rsr") as download:
        check_and_download()
        if exp_download:
            download.assert_called()
        else:
            download.assert_not_called()


@contextlib.contextmanager
def _fake_rsr_dir(tmp_path, rsr_version):
    new_config = {
        "rsr_dir": str(tmp_path),
        "download_from_internet": True,
    }
    with override_config(config_options=new_config):
        version_filename = str(tmp_path / RSR_DATA_VERSION_FILENAME)
        if rsr_version is not None:
            with open(version_filename, "w") as version_file:
                version_file.write(rsr_version)
        yield
