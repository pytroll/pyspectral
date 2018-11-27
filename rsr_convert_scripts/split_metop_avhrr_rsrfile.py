#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Adam.Dybbroe

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

"""Take the 'original' Metop-C AVHRR spectral responses from the file
AVHRR_A309_METOPC_SRF_PRELIMINARY.TXT and split it in one file per band and
convert the wavenumbers to wavelengths.

"""

import numpy as np
import os

DATAFILE = "/home/a000680/data/SpectralResponses/avhrr/AVHRR_A309_METOPC_SRF_PRELIMINARY.TXT"
OUTPUT_DIR = "/home/a000680/data/SpectralResponses/avhrr"

CH1_NAME = "Metop_C_A309C001.txt"
CH2_NAME = "Metop_C_A309C002.txt"
CH3A_NAME = "Metop_C_A309C03A.txt"
CH3B_NAME = "Metop_C_A309C03B.txt"
CH4_NAME = "Metop_C_A309C004.txt"
CH5_NAME = "Metop_C_A309C005.txt"

CH_FILES = {'ch1': CH1_NAME,
            'ch2': CH2_NAME,
            'ch3A': CH3A_NAME,
            'ch3B': CH3B_NAME,
            'ch4': CH4_NAME,
            'ch5': CH5_NAME
            }

HEADERLINE = "Wavelegth (um)      Normalized RSF"

with open(DATAFILE) as fpt:
    lines = fpt.readlines()

    idx = 0
    for counter, channel in enumerate(['ch1', 'ch2', 'ch3A', 'ch3B', 'ch4', 'ch5']):
        for line in lines[idx::]:
            if line.startswith('AVHRR'):
                break
            idx = idx + 1

        # print(lines[idx+2])
        wvn = []
        response = []
        for line in lines[idx+2:-1]:
            try:
                waven, resp = line.split()
            except ValueError:
                break

            wvn.append(float(waven))
            response.append(float(resp))
            idx = idx + 1

        # Convert from wavenumbers (cm-1) to wavelength (microns, um)
        wvl = 1./np.array(wvn) * 10000.0
        response = np.array(response)
        filename = os.path.join(OUTPUT_DIR, CH_FILES[channel])
        data = np.stack((wvl[::-1], response[::-1]), axis=-1)
        print(counter, filename)
        np.savetxt(filename, data, fmt="%8.6f     %10.8f", header=HEADERLINE)
