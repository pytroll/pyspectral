#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2026 Pytroll developers

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

"""Script to convert Pyspectral internal Terra/Aqua RSR files.

Read the internally generated hdf5 file with MODIS RSR and fix platform name
and write to a new file.

"""

import shutil
from pathlib import Path

import h5py

BASEDIR = "/data/pyspectral/"

if __name__ == "__main__":

    for satname in ['Aqua', 'Terra']:
        OLD_MODIS_FILE = Path(BASEDIR) / f'rsr_modis_EOS-{satname}.h5'
        NEW_MODIS_FILE = Path(BASEDIR) / f'rsr_modis_{satname}.h5'
        shutil.copy(OLD_MODIS_FILE, NEW_MODIS_FILE)

        remove_attrs = ["platform", "sat_number"]
        new_attrs = {
            "platform_name": satname,
        }

        with h5py.File(NEW_MODIS_FILE, "r+") as f:
            # Remove
            for key in remove_attrs:
                if key in f.attrs:
                    del f.attrs[key]

            # Add/update
            for key, value in new_attrs.items():
                f.attrs[key] = value
