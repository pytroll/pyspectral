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

import dask
import dask.array as da
import numpy as np
import pytest

from pyspectral.blackbody import blackbody, blackbody_rad2temp, blackbody_wn, blackbody_wn_rad2temp

RAD_11MICRON_300KELVIN = 9573176.935507433
RAD_11MICRON_301KELVIN = 9714686.576498277

# Radiances in wavenumber space (SI-units)
WN_RAD_11MICRON_300KELVIN = 0.00115835441353
WN_RAD_11MICRON_301KELVIN = 0.00117547716523

__unittest = True


class CustomScheduler(object):
    """Custom dask scheduler that raises an exception if dask is computed too many times."""

    def __init__(self, max_computes=1):
        """Set starting and maximum compute counts."""
        self.max_computes = max_computes
        self.total_computes = 0

    def __call__(self, dsk, keys, **kwargs):
        """Compute dask task and keep track of number of times we do so."""
        import dask
        self.total_computes += 1
        if self.total_computes > self.max_computes:
            raise RuntimeError("Too many dask computations were scheduled: {}".format(self.total_computes))
        return dask.get(dsk, keys, **kwargs)


class TestBlackbody:
    """Unit testing the blackbody function."""

    def test_blackbody(self):
        """Calculate the blackbody radiation from wavelengths and temperatures."""
        wavel = 11. * 1E-6
        black = blackbody(wavel, 300.)
        np.testing.assert_almost_equal(black[0], RAD_11MICRON_300KELVIN)
        temp1 = blackbody_rad2temp(wavel, black)
        np.testing.assert_almost_equal(temp1, 300.0, 4)

        black = blackbody(wavel, 301.)
        np.testing.assert_almost_equal(black, RAD_11MICRON_301KELVIN)
        temp2 = blackbody_rad2temp(wavel, black)
        np.testing.assert_almost_equal(temp2, 301.0, 4)

        tb_therm = np.array([[300., 301], [299, 298], [279, 286]])
        black = blackbody(10. * 1E-6, tb_therm)
        assert isinstance(black, np.ndarray)

    def test_blackbody_dask_wave_tuple(self):
        """Calculate the blackbody radiation from wavelengths and temperatures with dask arrays."""
        tb_therm = da.array([[300., 301], [299, 298], [279, 286]])
        with dask.config.set(scheduler=CustomScheduler(0)):
            black = blackbody(10. * 1E-6, tb_therm)
        assert isinstance(black, da.Array)
        assert black.dtype == np.float64

    @pytest.mark.parametrize("dtype", (np.float32, np.float64, float))
    def test_blackbody_dask_wave_array(self, dtype):
        """Test blackbody calculations with dask arrays as inputs."""
        tb_therm = da.array([[300., 301], [0., 298], [279, 286]], dtype=dtype)
        with dask.config.set(scheduler=CustomScheduler(0)):
            black = blackbody(da.array([10. * 1E-6, 11.e-6], dtype=dtype), tb_therm)
        assert isinstance(black, da.Array)
        assert black.dtype == dtype

    def test_blackbody_wn(self):
        """Calculate the blackbody radiation from wavenumbers and temperatures."""
        wavenumber = 90909.1  # 11 micron band
        black = blackbody_wn(wavenumber, 300.)
        np.testing.assert_almost_equal(black, WN_RAD_11MICRON_300KELVIN)
        temp1 = blackbody_wn_rad2temp(wavenumber, black)
        np.testing.assert_almost_equal(temp1, 300.0, 4)

        black = blackbody_wn(wavenumber, 301.)
        np.testing.assert_almost_equal(black, WN_RAD_11MICRON_301KELVIN)
        temp2 = blackbody_wn_rad2temp(wavenumber, black)
        np.testing.assert_almost_equal(temp2, 301.0, 4)

        t__ = blackbody_wn_rad2temp(wavenumber, np.array([0.001, 0.0009]))
        expected = [290.3276916, 283.76115441]
        np.testing.assert_almost_equal(t__[0], expected[0])
        np.testing.assert_almost_equal(t__[1], expected[1])

        radiances = np.array([0.001, 0.0009, 0.0012, 0.0018]).reshape(2, 2)
        t__ = blackbody_wn_rad2temp(wavenumber, radiances)
        expected = np.array([290.3276916, 283.76115441,
                             302.4181330, 333.1414164]).reshape(2, 2)
        np.testing.assert_almost_equal(t__[1, 1], expected[1, 1], 5)
        np.testing.assert_almost_equal(t__[0, 0], expected[0, 0], 5)
        np.testing.assert_almost_equal(t__[0, 1], expected[0, 1], 5)
        np.testing.assert_almost_equal(t__[1, 0], expected[1, 0], 5)

        np.testing.assert_allclose(t__, expected)

    def test_blackbody_wn_dask(self):
        """Test that blackbody rad2temp preserves dask arrays."""
        import dask
        import dask.array as da
        wavenumber = 90909.1  # 11 micron band
        radiances = da.from_array([0.001, 0.0009, 0.0012, 0.0018], chunks=2).reshape(2, 2)
        with dask.config.set(scheduler=CustomScheduler(0)):
            t__ = blackbody_wn_rad2temp(wavenumber, radiances)
        assert isinstance(t__, da.Array)
        t__ = t__.compute()
        expected = np.array([290.3276916, 283.76115441,
                             302.4181330, 333.1414164]).reshape(2, 2)
        np.testing.assert_almost_equal(t__[1, 1], expected[1, 1], 5)
        np.testing.assert_almost_equal(t__[0, 0], expected[0, 0], 5)
        np.testing.assert_almost_equal(t__[0, 1], expected[0, 1], 5)
        np.testing.assert_almost_equal(t__[1, 0], expected[1, 0], 5)

        np.testing.assert_allclose(t__, expected)
