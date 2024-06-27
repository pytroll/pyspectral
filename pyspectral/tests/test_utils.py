#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2022 Pytroll developers
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

"""Do the unit testing for the utils library."""
import contextlib
import logging
import os
import re
import tarfile
import tempfile
import unittest
import warnings
from io import BytesIO

import numpy as np
import pytest
import responses

from pyspectral import utils
from pyspectral.utils import are_instruments_identical, bytes2string, check_and_adjust_instrument_name, np2str

TEST_RSR = {'20': {}, }
TEST_RSR2 = {'20': {}, }
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

TEST_RSR2['20'] = TEST_RSR['20']['det-1']

RESULT_RSR = {'20': {}}
RESULT_RSR['20']['det-1'] = {}
RESULT_RSR['20']['det-1']['wavenumber'] = np.array([
    2529.38208008, 2533.8840332, 2540.390625, 2546.81494141,
    2553.30883789, 2559.88354492, 2566.40722656, 2573.02270508,
    2579.72949219, 2586.37451172, 2593.09375, 2599.87548828,
    2606.55371094, 2613.41674805, 2620.29760742, 2627.18286133,
    2634.06005859, 2641.07421875, 2648.06713867, 2655.03930664,
    2662.14794922, 2669.25170898, 2676.36572266, 2683.50805664,
    2690.69702148, 2697.95288086, 2705.29199219, 2712.56982422,
    2719.94970703, 2727.43554688, 2734.8605957, 2742.38012695,
    2749.9831543, 2757.48510742, 2765.21142578, 2768.24291992],
    dtype='float32')

RESULT_RSR['20']['det-1']['response'] = np.array([
    0.01, 0.01414, 0.02085, 0.02925, 0.04151, 0.07141,
    0.14852, 0.27762, 0.44715, 0.67429, 0.92676, 1.,
    0.94808, 0.94719, 0.94256, 0.91058, 0.91037, 0.95687,
    0.9541, 0.88922, 0.85412, 0.87697, 0.8661, 0.86008,
    0.92855, 0.96077, 0.81815, 0.59106, 0.33792, 0.16645,
    0.0849, 0.05028, 0.03226, 0.01987, 0.0118, 0.01],
    dtype='float32')


class _MockedRSR:
    def __init__(self, usedet=True):
        self.instrument = 'test_sensor'
        if usedet:
            self.tmp_rsr = TEST_RSR
        else:
            self.tmp_rsr = TEST_RSR2
        self.output_dir = tempfile.mkdtemp()

    def __call__(self, chan, plat):
        self.rsr = self.tmp_rsr[chan]
        return self


class RsrTestData(object):
    """Container for the RSR test datasets."""

    def __init__(self):
        """Initialize the class instance."""
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


class TestUtils(unittest.TestCase):
    """Unit testing the utils library functions."""

    def setUp(self):
        """Set up."""
        self.rsr = RsrTestData()

    def test_convert2wavenumber(self):
        """Testing the conversion of rsr from wavelength to wavenumber."""
        newrsr, info = utils.convert2wavenumber(TEST_RSR)
        unit = info['unit']
        self.assertEqual(unit, 'cm-1')
        self.assertTrue('wavenumber' in newrsr['20']['det-1'])
        self.assertFalse('wavelength' in newrsr['20']['det-1'])
        wvn_res = RESULT_RSR['20']['det-1']['wavenumber']
        wvn = newrsr['20']['det-1']['wavenumber']
        self.assertTrue(np.allclose(wvn_res, wvn))

    def test_convert2hdf5(self):
        """Test the conversion utility from original RSR to HDF5."""
        mocked_rsr_nodet = _MockedRSR(usedet=False)
        utils.convert2hdf5(mocked_rsr_nodet, 'Test_SAT', ['20'])
        fname = f'{mocked_rsr_nodet.output_dir}/rsr_test_sensor_Test_SAT.h5'
        self.assertTrue(os.path.exists(fname))
        try:
            os.remove(fname)
        except OSError:
            pass

        mocked_rsr_det = _MockedRSR(usedet=True)
        utils.convert2hdf5(mocked_rsr_det, 'Test_SAT', ['20'], detectors=['det-1'])
        fname = f'{mocked_rsr_det.output_dir}/rsr_test_sensor_Test_SAT.h5'
        self.assertTrue(os.path.exists(fname))
        try:
            os.remove(fname)
        except OSError:
            pass

    def test_get_bandname_from_wavelength(self):
        """Test the right bandname is found provided the wavelength in micro meters."""
        bname = utils.get_bandname_from_wavelength('abi', 0.4, self.rsr.rsr)
        self.assertEqual(bname, 'ch1')
        with self.assertRaises(AttributeError):
            utils.get_bandname_from_wavelength('abi', 0.5, self.rsr.rsr)

        bname = utils.get_bandname_from_wavelength('abi', 0.6, self.rsr.rsr, epsilon=0.05)
        self.assertEqual(bname, 'ch3')
        bname = utils.get_bandname_from_wavelength('abi', 0.7, self.rsr.rsr)
        self.assertEqual(bname, 'ch3')
        bname = utils.get_bandname_from_wavelength('abi', 0.8, self.rsr.rsr)
        self.assertEqual(bname, 'ch4')
        bname = utils.get_bandname_from_wavelength('abi', 1.0, self.rsr.rsr)
        self.assertEqual(bname, None)

        # Multiple bands returned due to large epsilon
        bname = utils.get_bandname_from_wavelength('abi', 11.1, self.rsr.rsr,
                                                   epsilon=1.0, multiple_bands=True)
        self.assertEqual(bname, ['ch13', 'ch14'])

        # uses generic channel mapping where '20' -> 'ch20'
        bandname = utils.get_bandname_from_wavelength('ufo', 3.7, TEST_RSR)
        self.assertEqual(bandname, 'ch20')

        bandname = utils.get_bandname_from_wavelength('ufo', 3.0, TEST_RSR)
        self.assertIsNone(bandname)

    @staticmethod
    def test_sort_data():
        """Test function sorting data into monotonically increasing values."""
        x_vals = np.array([1.0, 5.6, 30., 2.1, 108.2, 57.8, 1e9, 2.1])
        y_vals = np.array([45., 92., 20., 10., 15., 67., 108., 15.])

        x_sorted = np.array([1., 2.1, 5.6, 30, 57.8, 108.2, 1e9])
        y_sorted = np.array([45., 10., 92., 20., 67., 15., 108.])

        x_vals, y_vals = utils.sort_data(x_vals, y_vals)

        np.testing.assert_equal(x_vals, x_sorted)
        np.testing.assert_equal(y_vals, y_sorted)

    def test_get_wave_range(self):
        """Test the function that produces wavelength ranges from an RSR."""
        wvl_range = utils.get_wave_range(self.rsr.rsr['ch3']['det-1'], 0.15)
        expected_range = [0.59481323, 0.6393011276027835, 0.67512828]
        np.testing.assert_allclose(wvl_range, expected_range)

        wvl_range = utils.get_wave_range(self.rsr.rsr['ch3']['det-1'], 0.5)
        expected_range = [0.60931027, 0.6393011276027835, 0.67512828]
        np.testing.assert_allclose(wvl_range, expected_range)


@pytest.mark.parametrize(
    ("input_value", "exp_except"),
    [
        (np.bytes_("hey"), False),
        (np.array([np.bytes_("hey")]), False),
        (np.array(np.bytes_("hey")), False),
        ("hey", False),
        (np.array([np.bytes_("hey"), np.bytes_("hey")]), True),
        (5, True),
    ],
)
def test_np2str(input_value, exp_except):
    """Test the np2str function on different inputs."""
    if exp_except:
        with pytest.raises(ValueError):
            np2str(input_value)
    else:
        assert np2str(input_value) == "hey"


@pytest.mark.parametrize(
    ("input_value", "exp_result"),
    [
        (b"Hello", "Hello"),
        ("Hello", "Hello"),
        (np.bytes_("Hello"), "Hello"),
        (np.array(np.bytes_("Hello")), np.array(np.bytes_("Hello"))),
    ]
)
def test_bytes2string(input_value, exp_result):
    """Test the bytes2string function with different inputs."""
    assert bytes2string(input_value) == exp_result


def test_download_rsr_dry_run():
    """Test dry run of the download_rsr function."""
    with unittest.mock.patch("pyspectral.utils.requests") as requests_mock:
        utils.download_rsr(dry_run=True)
    requests_mock.assert_not_called()


def test_download_rsr(tmp_path):
    """Test basic usage of the download_rsr function."""
    tar_data = _create_fake_rsr_tarball_bytes()
    with responses.RequestsMock() as rsps:
        rsps.add(
            "GET",
            utils.HTTP_PYSPECTRAL_RSR,
            body=tar_data,
            status=200,
            content_type="application/octet-stream",
            headers={
                "Content-Length": str(len(tar_data)),
            },
        )
        utils.download_rsr(dest_dir=str(tmp_path))
    assert os.path.isfile(tmp_path / "PYSPECTRAL_RSR_VERSION")


def _create_fake_rsr_tarball_bytes():
    file_obj = BytesIO()

    with tarfile.open(mode="w:gz", fileobj=file_obj) as rsr_tar:
        info = tarfile.TarInfo(utils.RSR_DATA_VERSION_FILENAME)
        info.size = len(utils.RSR_DATA_VERSION)
        rsr_tar.addfile(info, BytesIO(utils.RSR_DATA_VERSION.encode("ascii")))

    file_obj.seek(0)
    return file_obj.read()


def test_download_luts_dry_run():
    """Test a dry run of the download_luts function."""
    with unittest.mock.patch("pyspectral.utils.requests") as requests_mock:
        utils.download_luts(dry_run=True)
    requests_mock.assert_not_called()


@pytest.mark.parametrize(
    ("aerosol_types", "aerosol_type", "exp_warning"),
    [
        (None, None, False),
        (["desert_aerosol"], None, False),
        (None, "desert_aerosol", True),
    ]
)
def test_download_luts(tmp_path, aerosol_types, aerosol_type, exp_warning):
    """Test basic usage of the download_luts function."""
    atypes_to_create = _atypes_to_create(aerosol_types, aerosol_type)
    tar_data = _create_fake_lut_tarball_bytes(aerosol_types=atypes_to_create)
    with responses.RequestsMock() as rsps:
        rsps.add(
            "GET",
            re.compile(re.escape(utils.LUT_URL_PREFIX) + r"_.+\.tgz"),
            body=tar_data,
            status=200,
            content_type="application/octet-stream",
            headers={
                "Content-Length": str(len(tar_data)),
            },
        )
        with _fake_get_config(tmp_path), warnings.catch_warnings(record=True) as warns:
            utils.download_luts(aerosol_types=aerosol_types, aerosol_type=aerosol_type)
    _check_user_warning(warns, exp_warning)
    _check_expected_aerosol_files(atypes_to_create, tmp_path)


def _atypes_to_create(aerosol_types, aerosol_type):
    if aerosol_types:
        return aerosol_types
    if aerosol_type is None:
        return utils.AEROSOL_TYPES
    return [aerosol_type]


def _create_fake_lut_tarball_bytes(aerosol_types):
    file_obj = BytesIO()

    with tarfile.open(mode="w:gz", fileobj=file_obj) as rsr_tar:
        for aerosol_type in aerosol_types:
            version_fn = utils.ATM_CORRECTION_LUT_VERSION[aerosol_type]["filename"]
            version_value = utils.ATM_CORRECTION_LUT_VERSION[aerosol_type]["version"]
            info = tarfile.TarInfo(version_fn)
            info.size = len(version_value)
            rsr_tar.addfile(info, BytesIO(version_value.encode("ascii")))

    file_obj.seek(0)
    return file_obj.read()


@contextlib.contextmanager
def _fake_get_config(tmp_path):
    def _get_config():
        return {
            "rayleigh_dir": str(tmp_path),
            "rsr_dir": str(tmp_path),
        }
    with unittest.mock.patch("pyspectral.utils.get_config") as get_config:
        get_config.side_effect = _get_config
        yield


def _check_user_warning(warns, exp_warning):
    all_user_warnings = [warn_msg for warn_msg in warns if issubclass(warn_msg.category, UserWarning)]
    all_matching_warnings = [warn_msg for warn_msg in all_user_warnings if "aerosol_type" in str(warn_msg.message)]
    assert len(all_matching_warnings) == (1 if exp_warning else 0)


def _check_expected_aerosol_files(atypes_to_create, tmp_path):
    for aerosol_type in utils.AEROSOL_TYPES:
        atype_fn = tmp_path / aerosol_type / utils.ATM_CORRECTION_LUT_VERSION[aerosol_type]["filename"]
        if aerosol_type in atypes_to_create:
            assert atype_fn.is_file()
        else:
            assert not atype_fn.is_file()


@pytest.mark.parametrize(
    ("platform_name", "input_value_sensor", "exp_sensor_name"),
    [
        ('Metop-C', 'avhrr/3', 'avhrr3'),
        ('NOAA-19', 'avhrr/3', 'avhrr3'),
        ('NOAA-12', 'avhrr/2', 'avhrr2'),
        ('TIROS-N', 'avhrr/1', 'avhrr1'),
        ('Metop-C', 'avhrr-3', 'avhrr3'),
        ('NOAA-12', 'avhrr-2', 'avhrr2'),
        ('TIROS-N', 'avhrr-1', 'avhrr1'),
    ],
)
def test_check_and_adjust_instrument_name_instrument_okay(platform_name, input_value_sensor, exp_sensor_name):
    """Test the checking and adjusting of the instrument name."""
    res = check_and_adjust_instrument_name(platform_name, input_value_sensor)
    assert res == exp_sensor_name


@pytest.mark.parametrize(
    ("platform_name", "input_value_sensor", "exp_sensor_name"),
    [
        ('GOES-16', 'Idontknow', 'abi'),
        ('FY-4B', 'unknown', 'agri'),
        ('Meteosat-12', 'seviri', 'fci'),
    ],
)
def test_check_and_adjust_instrument_name_instrument_name_inconsistent(caplog,
                                                                       platform_name,
                                                                       input_value_sensor,
                                                                       exp_sensor_name):
    """Test the checking and adjusting of the instrument name."""
    with caplog.at_level(logging.WARNING):
        _ = check_and_adjust_instrument_name(platform_name, input_value_sensor)

    log_output = "Inconsistent instrument/satellite input - instrument set to {instr}".format(instr=exp_sensor_name)
    assert log_output in caplog.text


@pytest.mark.parametrize(
    ("platform_name", "input_value_sensor", "exp_sensor_name"),
    [
        ('GOES-16', 'abi', 'abi'),
        ('FY-4B', 'ghi', 'ghi'),
        ('Meteosat-12', 'fci', 'fci'),
    ],
)
def test_check_and_adjust_instrument_name_correct(platform_name, input_value_sensor, exp_sensor_name):
    """Check instrument name is not changed if correct."""
    assert check_and_adjust_instrument_name(platform_name, input_value_sensor) == exp_sensor_name


def test_are_instruments_identical():
    """Test that error is raised if non-string is passed to the function."""
    res = are_instruments_identical('thing1', 'thing1')
    assert res is True
    res = are_instruments_identical('thing1', 'thing2')
    assert res is False

    with pytest.raises(ValueError):
        are_instruments_identical(['thing1', 'thing3'], 'thing2')
