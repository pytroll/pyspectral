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

"""
Draft limb-cooling correction methods - work in progress.

Depending on the satellite sensor spectral band the upwelling infrared
radiation in a cloudfree atmosphere will be subject to absorption by
atmospherical molecules, mainly water vapour, Ozone, CO2 and other trace
gases. This absorption is depending on the observational path length. Usually
the satellite signal is subject to what is referred to as limb cooling, such
that observed brightness temperatures under large view angles are lower than
those under smaller view angles.

This code seek to correct for this cooling, so that it is possible to get a
more consistent looking satellite image also when using imager bands which are
not true window channels, but rather subject to some absorption ('dirty window
channel').

The goal is eventually to do this atmospheric correction with the use of off
line Radiative Transfer Model simulations giving look up tables of atmospheric
absorption for various standard atmospheres and satellite zenith angles and
spectral bands.

But, for now, we apply and old parametric method implemented at DWD since long
ago:

J.Asmus (August 2017): 'Some information to our atmospheric correction. This
routine is very old, as Katja told. It running in DWD since around 1989 at
first on DEC Micro VAX 4000-300, later on SGI workstation (O2) both as FORTRAN
program, later in CineSat and now in PyTroll. This correction is very simple
but it had to run on a Micro VAX.  The idea was to get some more realistic
temperatures in the higher latitudes. The source for this atmospheric
correction must be a paper from the US Air Force in the 1960 or 1970 years
(?). Unfortunaly I have no more information about the source and the colleagues
from this time are not longer at DWD.'

"""


import numpy as np

try:
    import dask.array as da
except ImportError:
    da = None


import logging

LOG = logging.getLogger(__name__)


class AtmosphericalCorrection(object):
    """IR atmospherical correction.

    Container for the IR atmospherical correction of satellite imager IR (dirty)
    window bands

    """

    def __init__(self, platform_name, sensor, **kwargs):
        """Atmosphere correction in the infrared."""
        self.platform_name = platform_name
        self.sensor = sensor
        self.coeff_filename = None

        if 'atmosphere' in kwargs:
            atm_type = kwargs['atmosphere']
        else:
            atm_type = None

        if atm_type:
            raise AttributeError("Atmosphere type %s not supported", atm_type)

        LOG.info("Atmospherical correction by old DWD parametric method...")

    def get_correction(self, sat_zenith, bandname, data):
        """Get the correction depending on satellite zenith angle and band."""
        # From band name we will eventually need the effective wavelength
        # and then use that to find the atm contribution depending on zenith
        # angle from a LUT
        return viewzen_corr(data.copy(), sat_zenith)


def viewzen_corr(data, view_zen):
    """Apply satellite-zenith angle dependent correction.

    Apply atmospheric correction on the given *data* using the
    specified satellite zenith angles (*view_zen*). Both input data
    are given as 2-dimensional Numpy (masked) arrays, and they should
    have equal shapes.
    The *data* array will be changed in place and has to be copied before.

    """
    def ratio(value, v_null, v_ref):
        return (value - v_null) / (v_ref - v_null)

    def tau0(t):
        T_0 = 210.0
        T_REF = 320.0
        TAU_REF = 9.85
        return (1 + TAU_REF)**ratio(t, T_0, T_REF) - 1

    def tau(t):
        T_0 = 170.0
        T_REF = 295.0
        TAU_REF = 1.0
        M = 4
        return TAU_REF * ratio(t, T_0, T_REF)**M

    def delta(z):
        Z_0 = 0.0
        Z_REF = 70.0
        DELTA_REF = 6.2
        return (1 + DELTA_REF)**ratio(z, Z_0, Z_REF) - 1

    is_dask_data = hasattr(data, 'compute') or hasattr(view_zen, 'compute')

    if is_dask_data:
        data_tau0 = data + tau0(data)
        data_tau_delta = data + (tau(data) * delta(view_zen))
        dask_data = da.where(view_zen == 0, data_tau0,
                             da.where((view_zen > 0) & (view_zen < 90),
                                      data_tau_delta, data))
        return dask_data
    # expect numpy types otherwise
    y0, x0 = np.ma.where(view_zen == 0)
    data[y0, x0] += tau0(data[y0, x0])

    y, x = np.ma.where((view_zen > 0) & (view_zen < 90) & (~data.mask))
    data[y, x] += tau(data[y, x]) * delta(view_zen[y, x])
    return data


if __name__ == "__main__":
    this = AtmosphericalCorrection('Suomi-NPP', 'viirs')
    SHAPE = (1000, 3000)
    NDIM = SHAPE[0] * SHAPE[1]
    SATZ = np.ma.arange(NDIM).reshape(SHAPE) * 60. / float(NDIM)
    TBS = np.ma.arange(NDIM).reshape(SHAPE) * 80.0 / float(NDIM) + 220.
    atm_corr = this.get_correction(SATZ, 'M4', TBS)
    atm_corr = this.get_correction(da.from_array(SATZ), 'M4', da.from_array(TBS))
