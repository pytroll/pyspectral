#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Adam.Dybbroe

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

"""Compare the content of two hdf5 files with rsr data
"""

import pdb
import numpy as np
from pyspectral.rsr_reader import RelativeSpectralResponse

#FILE1 = '/home/a000680/data/pyspectral/rsr_viirs_Suomi-NPP.h5'
#FILE2 = '/home/a000680/data/pyspectral/BACKUP_rsr_viirs_Suomi-NPP.h5'
FILE1 = "/home/a000680/data/pyspectral/OLDrsr_ahi_Himawari-8.h5"
FILE2 = "/home/a000680/data/pyspectral/rsr_ahi_Himawari-8.h5"

rsr_a = RelativeSpectralResponse(filename=FILE1)
rsr_b = RelativeSpectralResponse(filename=FILE2)

for band in rsr_a.rsr:
    for det in rsr_a.rsr[band]:
        wvl1 = rsr_a.rsr[band][det]['wavelength']
        wvl2 = rsr_b.rsr[band][det]['wavelength']
        try:
            if not np.allclose(wvl1, wvl2):
                pdb.set_trace()
        except ValueError:
            pdb.set_trace()
        resp1 = rsr_a.rsr[band][det]['response']
        resp2 = rsr_b.rsr[band][det]['response']
        try:
            if not np.allclose(resp1, resp2):
                pdb.set_trace()
        except ValueError:
            pdb.set_trace()
        cw1 = rsr_a.rsr[band][det]['central_wavelength']
        cw2 = rsr_b.rsr[band][det]['central_wavelength']
        if np.abs(cw1 - cw2) > 0.00001:
            pdb.set_trace()
