#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2022 Pytroll developers
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

"""Unit testing the generic rsr hdf5 reader."""
from __future__ import annotations

import contextlib
import os.path
import unittest

import numpy as np
import pytest
import xarray as xr

from pyspectral.rsr_reader import RelativeSpectralResponse, RSRDict
from pyspectral.testing import mock_pyspectral_downloads
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

DIR_PATH_ITEMS = ['test', 'path', 'to', 'rsr', 'data']
TEST_CONFIG = {}

TEST_RSR_DIR = os.path.join(*DIR_PATH_ITEMS)
TEST_CONFIG['rsr_dir'] = TEST_RSR_DIR


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


def test_convert():
    """Test the conversion method."""
    with mock_pyspectral_downloads() as download_mocks:
        load_rsr_info = download_mocks["load_rsr_info"]
        load_rsr_info.side_effect = None
        load_rsr_info.return_value = {
            "description": "",
            "instrument": "modis",
            "platform_name": "EOS-Aqua",
            "band_names": list(TEST_RSR.keys()),
            "rsr": TEST_RSR,
        }
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        test_rsr.convert()
        np.testing.assert_allclose(test_rsr.rsr["20"]["det-1"]["central_wavenumber"], 2647.397, atol=1e-3)
        np.testing.assert_allclose(test_rsr.rsr["20"]["det-1"][WAVE_NUMBER], RESULT_WVN_RSR, 5)
        assert test_rsr._wavespace == WAVE_NUMBER

        with pytest.raises(NotImplementedError):
            test_rsr.convert()


def test_integral():
    """Test the calculation of the integral of the spectral responses."""
    with mock_pyspectral_downloads() as download_mocks:
        load_rsr_info = download_mocks["load_rsr_info"]
        load_rsr_info.side_effect = None
        load_rsr_info.return_value = {
            "description": "",
            "instrument": "modis",
            "platform_name": "EOS-Aqua",
            "band_names": list(TEST_RSR2.keys()),
            "rsr": TEST_RSR,
        }
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        test_rsr.rsr = TEST_RSR2
        res = test_rsr.integral("20")
        np.testing.assert_almost_equal(res["det-1"], 0.185634, 6)


def test_metadata_from_hdf5_with_platform_instrument():
    """Test metadata is accepted from HDF5 file."""
    with mock_pyspectral_downloads() as download_mocks:
        load_rsr_info = download_mocks["load_rsr_info"]
        load_rsr_info.side_effect = None
        load_rsr_info.return_value = {
            "description": "ABCD",
            "instrument": "modis123",
            "platform_name": "EOS-Aqua456",
            "band_names": list(TEST_RSR2.keys()),
            "rsr": TEST_RSR,
        }
        test_rsr = RelativeSpectralResponse("EOS-Aqua", "modis")
        assert test_rsr.description == "ABCD"
        # platform and instrument are not overwritten by file content
        assert test_rsr.platform_name == "EOS-Aqua"
        assert test_rsr.instrument == "modis"
        assert test_rsr.band_names == list(TEST_RSR2.keys())
        assert test_rsr.filename.name == "rsr_modis_EOS-Aqua.h5"


def test_get_band_from_wavelength():
    """Test metadata is accepted from HDF5 file."""
    with mock_pyspectral_downloads() as download_mocks:
        load_rsr_info = download_mocks["load_rsr_info"]
        load_rsr_info.side_effect = None
        load_rsr_info.return_value = {
            "description": "ABCD",
            "instrument": "modis123",
            "platform_name": "EOS-Aqua456",
            "band_names": list(TEST_RSR2.keys()),
            "rsr": TEST_RSR,
        }
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


class MyHdf5Mock:
    """A Mock for the RSR data normally stored in a HDF5 file."""

    def __init__(self, attrs):
        """Initialize the mock class."""
        self.attrs = attrs


def _create_fake_modis_data():
    """Initialise the tests."""
    bandnames = np.array([b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'10', b'11',
                          b'12', b'13', b'14', b'15', b'16', b'17', b'18', b'19', b'20',
                          b'21', b'22', b'23', b'24', b'25', b'26', b'27', b'28', b'29',
                          b'30', b'31', b'32', b'33', b'34', b'35', b'36'], dtype='|S2')
    hdf5_attrs_aqua_modis = {'band_names': bandnames,
                             'description': 'Relative Spectral Responses for MODIS',
                             'platform': 'eos',
                             'sat_number': 2}
    modis_bandnames = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
                            '31', '32', '33', '34', '35', '36']

    return MyHdf5Mock(hdf5_attrs_aqua_modis), modis_bandnames


def _create_fake_modis_data_bytes():
    data, modis_bandnames = _create_fake_modis_data()
    data.attrs.update({
        "description": b"Relative Spectral Responses for MODIS",
        "platform": b"eos",
        "sat_number": 2,
    })
    return MyHdf5Mock(data), modis_bandnames


def _create_fake_viirs_data():
    bandnames = np.array([b'M1', b'M2', b'M3', b'M4', b'M5', b'M6', b'M7', b'M8', b'M9',
                          b'M10', b'M11', b'M12', b'M13', b'M14', b'M15', b'M16', b'I1',
                          b'I2', b'I3', b'I4', b'I5', b'DNB'], dtype='|S3')

    hdf5_attrs_noaa20_viirs = {'band_names': bandnames,
                               'description': b'Relative Spectral Responses for VIIRS',
                               'platform_name': b'NOAA-20',
                               'sensor': b'viirs'}
    viirs_bandnames = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10',
                       'M11', 'M12', 'M13', 'M14', 'M15', 'M16',
                       'I1', 'I2', 'I3', 'I4', 'I5', 'DNB']
    viirs_detector_names = ['det-1', 'det-2', 'det-3', 'det-4', 'det-5',
                            'det-6', 'det-7', 'det-8', 'det-9', 'det-10',
                            'det-11', 'det-12', 'det-13', 'det-14', 'det-15',
                            'det-16']
    viirs_rsr_data = xr.Dataset({'wavelength': xr.DataArray(np.arange(10)),
                                 'response': xr.DataArray(np.arange(10))})
    viirs_rsr_data.attrs['central_wavelength'] = 100.0
    viirs_rsr_data['wavelength'].attrs['scale'] = 0.01

    return MyHdf5Mock(hdf5_attrs_noaa20_viirs), viirs_bandnames, viirs_detector_names


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
def test_get_rsr_from_platform_and_instrument(platform_name, instrument, exp_filename, exp_instrument):
    """Test getting the rsr filename correct when specifying the platform and instrument names."""
    with mock_pyspectral_downloads():
        test_rsr = RelativeSpectralResponse(platform_name, instrument)
        assert test_rsr.platform_name == platform_name
        assert test_rsr.instrument == exp_instrument
        assert test_rsr.filename.name == exp_filename


@pytest.mark.parametrize(
    ("version", "exp_download"),
    [
        (RSR_DATA_VERSION, False),
        ("v1.0.0", True),
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
    with _fake_get_config(tmp_path):
        version_filename = str(tmp_path / RSR_DATA_VERSION_FILENAME)
        with open(version_filename, "w") as version_file:
            version_file.write(rsr_version)
        yield


@contextlib.contextmanager
def _fake_get_config(tmp_path):
    def _get_config():
        return {
            "rayleigh_dir": str(tmp_path),
            "rsr_dir": str(tmp_path),
            "download_from_internet": True,
        }
    with unittest.mock.patch("pyspectral.rsr_reader.get_config") as get_config:
        get_config.side_effect = _get_config
        yield
