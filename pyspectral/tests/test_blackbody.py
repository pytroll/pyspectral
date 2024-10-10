#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2012, 2022 Pytroll developers
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

"""Unit testing the Blackbody/Plack radiation derivation."""

import warnings

import dask
import dask.array as da
import numpy as np
import pytest

from pyspectral.blackbody import blackbody, blackbody_rad2temp, blackbody_wn, blackbody_wn_rad2temp
from pyspectral.tests.unittest_helpers import ComputeCountingScheduler

RAD_11MICRON_300KELVIN = 9573176.935507433
RAD_11MICRON_301KELVIN = 9714686.576498277

# Radiances in wavenumber space (SI-units)
WN_RAD_11MICRON_300KELVIN = 0.00115835441353
WN_RAD_11MICRON_301KELVIN = 0.00117547716523

__unittest = True


class TestBlackbody:
    """Unit testing the blackbody function."""

    def test_blackbody(self):
        """Calculate the blackbody radiation from wavelengths and temperatures."""
        wavel = 11. * 1E-6
        black = blackbody(wavel, 300.)
        assert black == pytest.approx(RAD_11MICRON_300KELVIN)
        temp1 = blackbody_rad2temp(wavel, black)
        assert temp1 == pytest.approx(300.0, 4)

        black = blackbody(wavel, 301.)
        assert black == pytest.approx(RAD_11MICRON_301KELVIN)
        temp2 = blackbody_rad2temp(wavel, black)
        assert temp2 == pytest.approx(301.0, 4)

        tb_therm = np.array([[300., 301], [299, 298], [279, 286]])
        black = blackbody(10. * 1E-6, tb_therm)
        assert isinstance(black, np.ndarray)

    def test_blackbody_dask_wave_tuple(self):
        """Calculate the blackbody radiation from wavelengths and temperatures with dask arrays."""
        tb_therm = da.array([[300., 301], [299, 298], [279, 286]])
        with dask.config.set(scheduler=ComputeCountingScheduler(0)):
            black = blackbody(10. * 1E-6, tb_therm)
        assert isinstance(black, da.Array)
        assert black.dtype == np.float64

    @pytest.mark.parametrize("dtype", (np.float32, np.float64, float))
    def test_blackbody_dask_wave_array(self, dtype):
        """Test blackbody calculations with dask arrays as inputs."""
        tb_therm = da.array([[300., 301], [0., 298], [279, 286]], dtype=dtype)
        with dask.config.set(scheduler=ComputeCountingScheduler(0)):
            black = blackbody(da.array([10. * 1E-6, 11.e-6], dtype=dtype), tb_therm)
        assert isinstance(black, da.Array)
        assert black.dtype == dtype

    def test_blackbody_wn(self):
        """Calculate the blackbody radiation from wavenumbers and temperatures."""
        wavenumber = 90909.1  # 11 micron band
        black = blackbody_wn(wavenumber, 300.)
        assert black == pytest.approx(WN_RAD_11MICRON_300KELVIN)
        temp1 = blackbody_wn_rad2temp(wavenumber, black)
        assert temp1 == pytest.approx(300.0, 4)

        black = blackbody_wn(wavenumber, 301.)
        assert black == pytest.approx(WN_RAD_11MICRON_301KELVIN)
        temp2 = blackbody_wn_rad2temp(wavenumber, black)
        assert temp2 == pytest.approx(301.0, 4)

        t__ = blackbody_wn_rad2temp(wavenumber, np.array([0.001, 0.0009]))
        expected = [290.3276916, 283.76115441]
        np.testing.assert_allclose(t__, expected)

        radiances = np.array([0.001, 0.0009, 0.0012, 0.0018]).reshape(2, 2)
        t__ = blackbody_wn_rad2temp(wavenumber, radiances)
        expected = np.array([290.3276916, 283.76115441,
                             302.4181330, 333.1414164]).reshape(2, 2)
        np.testing.assert_allclose(t__, expected)

    def test_blackbody_wn_dask(self):
        """Test that blackbody rad2temp preserves dask arrays."""
        import dask
        import dask.array as da
        wavenumber = 90909.1  # 11 micron band
        radiances = da.from_array([0.001, 0.0009, 0.0012, 0.0018], chunks=2).reshape(2, 2)
        with dask.config.set(scheduler=ComputeCountingScheduler(0)):
            t__ = blackbody_wn_rad2temp(wavenumber, radiances)
        assert isinstance(t__, da.Array)
        t__ = t__.compute()
        expected = np.array([290.3276916, 283.76115441,
                             302.4181330, 333.1414164]).reshape(2, 2)
        np.testing.assert_allclose(t__, expected)

    def test_ignore_division_warning(self):
        """Test that zero division warning is ignored."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _ = blackbody_rad2temp(np.ones(1), np.zeros(1))
            _ = blackbody_wn_rad2temp(np.ones(1), np.zeros(1))
            _ = blackbody(np.ones(2), np.array([0, 1]))
            _ = blackbody_wn(np.ones(2), np.array([0, 1]))
