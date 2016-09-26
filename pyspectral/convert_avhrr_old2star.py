#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

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

"""Convert NOAA 15 Spectral responses to new NOAA STAR format
"""

import numpy as np
import pandas as pd

VIS_FILE = "/home/a000680/data/SpectralResponses/avhrr/NOAA15_AVHRR_responses_VIS.txt"
IR_FILE = "/home/a000680/data/SpectralResponses/avhrr/NOAA15_AVHRR_responses_IR.txt"

VIS_FIELDS = ['wvl1', 'resp1', 'wvl2', 'resp2', 'wvl3a', 'resp3a']
IR_FIELDS = ['wvl3b', 'resp3b', 'wvl4', 'resp4', 'wvl5', 'resp5']

OUTPUT_FILES = {'wvl1': 'NOAA_15_A302xx01.txt',
                'wvl2': 'NOAA_15_A302xx02.txt',
                'wvl3a': 'NOAA_15_A302xx3A.txt',
                'wvl3b': 'NOAA_15_A302xx3B.txt',
                'wvl4': 'NOAA_15_A302xx04.txt',
                'wvl5': 'NOAA_15_A302xx05.txt'
                }


def unpack_data(filename, fields):
    data = pd.read_csv(filename,
                       delim_whitespace=True,
                       names=fields,
                       false_values='-')

    for i in range(0, len(fields), 2):
        wvl = data[:][fields[i]].values
        resp = data[:][fields[i + 1]].values

        wvl = np.ma.masked_where(
            wvl == '-', wvl).compressed().astype('float32')
        resp = np.ma.masked_where(
            resp == '-', resp).compressed().astype('float32') / 100.0

        hdline = "Wavelegth (um)  Normalized RSF"
        np.savetxt(OUTPUT_FILES[fields[i]],
                   np.transpose([wvl.transpose(), resp.transpose()]),
                   fmt='%3.6f',
                   delimiter=' ' * 8,
                   header=hdline, newline='\n')

    return

if __name__ == "__main__":

    unpack_data(IR_FILE, IR_FIELDS)
    unpack_data(VIS_FILE, VIS_FIELDS)
