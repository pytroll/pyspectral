#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Pytroll developers
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

"""Read the NOAA AVHRR/1 relative spectral response functions.

Data from NOAA: AVHRR1_SRF_only.xls
"""

import os
from xlrd import open_workbook
from pyspectral.config import get_config
from pyspectral.utils import get_central_wave
import numpy as np
import pkg_resources
import logging
import h5py


LOG = logging.getLogger(__name__)

AVHRR_BAND_NAMES = {'avhrr/1': ['ch1', 'ch2', 'ch3', 'ch4']}
AVHRR1_SATELLITES = ['TIROS-N', 'NOAA-6', 'NOAA-8', 'NOAA-10']

DATA_PATH = pkg_resources.resource_filename('pyspectral', 'data/')

CHANNEL_NAMES = {'A101C001': 'ch1',
                 'A101C002': 'ch2',
                 'A101C003': 'ch3',
                 'A101C004': 'ch4',
                 'A102C001': 'ch1',
                 'A102C002': 'ch2',
                 'A102C003': 'ch3',
                 'A102C004': 'ch4',
                 'A103C001': 'ch1',
                 'A103C002': 'ch2',
                 'A103C003': 'ch3',
                 'A103C004': 'ch4',
                 'A104C001': 'ch1',
                 'A104C002': 'ch2',
                 'A104C003': 'ch3',
                 'A104C004': 'ch4'}


class AvhrrRSR():
    """Container for the NOAA AVHRR-1 RSR data."""

    def __init__(self, wavespace='wavelength'):
        """Initialize the AVHRR-1 RSR class."""
        options = get_config()

        self.avhrr_path = options['avhrr/1'].get('path')
        if not os.path.exists(self.avhrr_path):
            self.avhrr1_path = os.path.join(
                DATA_PATH, options['avhrr/1'].get('filename'))

        self.output_dir = options.get('rsr_dir', './')

        self.rsr = {}
        for satname in AVHRR1_SATELLITES:
            self.rsr[satname] = {}
            for chname in AVHRR_BAND_NAMES['avhrr/1']:
                self.rsr[satname][chname] = {'wavelength': None, 'response': None}

        self._load()
        self.wavespace = wavespace
        if wavespace not in ['wavelength', 'wavenumber']:
            raise AttributeError("wavespace has to be either " +
                                 "'wavelength' or 'wavenumber'!")

        self.unit = 'micrometer'
        if wavespace == 'wavenumber':
            # Convert to wavenumber:
            self.convert2wavenumber()

    def _load(self, scale=1.0):
        """Load the AVHRR RSR data for the band requested."""
        wb_ = open_workbook(self.avhrr_path)

        sheet_names = []
        for sheet in wb_.sheets():
            if sheet.name in ['Kleespies Data', ]:
                print("Skip sheet...")
                continue

            ch_name = CHANNEL_NAMES.get(sheet.name.strip())
            if not ch_name:
                break

            sheet_names.append(sheet.name.strip())

            header = sheet.col_values(0, start_rowx=0, end_rowx=2)
            platform_name = header[0].strip("# ")
            unit = header[1].split("Wavelength (")[1].strip(")")

            scale = get_scale_from_unit(unit)

            wvl = sheet.col_values(0, start_rowx=2)
            is_comment = True
            idx = 0
            while is_comment:
                item = wvl[::-1][idx]
                if isinstance(item, str):
                    idx = idx+1
                else:
                    break

            ndim = len(wvl) - idx
            wvl = wvl[0:ndim]

            if platform_name == "TIROS-N":
                wvl = adjust_typo_avhrr1_srf_only_xls_file(platform_name, wvl)

            response = sheet.col_values(1, start_rowx=2, end_rowx=2+ndim)

            wavelength = np.array(wvl) * scale
            response = np.array(response)

            self.rsr[platform_name][ch_name]['wavelength'] = wavelength
            self.rsr[platform_name][ch_name]['response'] = response


def adjust_typo_avhrr1_srf_only_xls_file(platform_name, wvl):
    """Adjust typo in wavelength: 640 should most certainly have been 840 in the AVHRR1_SRF_only.xls."""
    epsilon = 0.01
    for idx, wavel in enumerate(wvl[1::]):
        if wvl[idx] > wavel and abs(wavel-640.0) < epsilon:
            wvl[idx+1] = 840.0
    return wvl


def get_scale_from_unit(unit):
    """Get the scaling factor to go from unit to micrometers."""
    unit2scale = {'Å': 0.0001, 'nm': 0.001}
    return unit2scale.get(unit)


def generate_avhrr1_file(avhrr1, platform_name):
    """Generate the relative response functions for one AVHRR-1 ensor.

    Format is the pyspectral internal common format.
    """
    filename = os.path.join(avhrr1.output_dir, "rsr_avhrr1_{sat}.h5".format(sat=platform_name))

    with h5py.File(filename, "w") as h5f:

        h5f.attrs['description'] = 'Relative Spectral Responses for AVHRR/1'
        h5f.attrs['platform_name'] = platform_name
        bandnames = avhrr1.rsr[platform_name].keys()
        h5f.attrs['band_names'] = [str(key) for key in bandnames]

        for chname in bandnames:
            grp = h5f.create_group(chname)

            wvl = avhrr1.rsr[platform_name][chname]['wavelength']
            rsp = avhrr1.rsr[platform_name][chname]['response']
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = avhrr1.rsr[platform_name][chname]['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = 1e-06
            dset[...] = arr
            arr = avhrr1.rsr[platform_name][chname]['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr


def run_avhrr1():
    """Create the AVHRR-1 relative spectral response files."""
    avhrr_obj = AvhrrRSR()
    for platform_name in ["NOAA-10", "NOAA-8", "NOAA-6", "TIROS-N"]:
        generate_avhrr1_file(avhrr_obj, platform_name)


if __name__ == "__main__":
    run_avhrr1()
