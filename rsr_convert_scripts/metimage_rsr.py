#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Adam.Dybbroe

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

"""Read the preliminary MetImage relative spectral response functions.
Data from the NWPSAF, These are very early theoretical and idealized versions,
derived from specifications I assume.

"""

import os
import numpy as np
from pyspectral.utils import get_central_wave
from pyspectral.raw_reader import InstrumentRSR
import logging

LOG = logging.getLogger(__name__)

METIMAGE_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5',
                       'ch6', 'ch7', 'ch8', 'ch9', 'ch10',
                       'ch11', 'ch12', 'ch13', 'ch14', 'ch15',
                       'ch16', 'ch17', 'ch18', 'ch19', 'ch20']


class MetImageRSR(InstrumentRSR):

    """Container for the EPS-SG MetImage RSR data"""

    def __init__(self, bandname, platform_name):

        super(MetImageRSR, self).__init__(
            bandname, platform_name, METIMAGE_BAND_NAMES)

        self.instrument = 'metimage'
        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

        self.unit = 'micrometer'
        self.wavespace = 'wavelength'

    def _load(self, scale=1.0):
        """Load the MetImage RSR data for the band requested"""
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavenumber',
                                    'response'],
                             skip_header=4)

        # Data are wavenumbers in cm-1:
        wavelength = 1. / data['wavenumber'] * 10000.
        response = data['response']

        # The real MetImage has 24 detectors. However, for now we store the
        # single rsr as 'detector-1', indicating that there will be multiple
        # detectors in the future:
        detectors = {}
        detectors['det-1'] = {'wavelength': wavelength, 'response': response}
        self.rsr = detectors


def generate_metimage_file(platform_name):
    """Retrieve original RSR data and convert to internal hdf5 format.
    """
    import h5py

    bandnames = METIMAGE_BAND_NAMES
    instr = MetImageRSR(bandnames[0], platform_name)
    instr_name = instr.instrument.replace('/', '')
    filename = os.path.join(instr.output_dir,
                            "rsr_{0}_{1}.h5".format(instr_name,
                                                    platform_name))

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = ('Relative Spectral Responses for ' +
                                    instr.instrument.upper())
        h5f.attrs['platform_name'] = platform_name
        h5f.attrs['band_names'] = bandnames

        for chname in bandnames:
            metimage = MetImageRSR(chname, platform_name)
            grp = h5f.create_group(chname)
            grp.attrs['number_of_detectors'] = len(metimage.rsr.keys())
            # Loop over each detector to check if the sampling wavelengths are
            # identical:
            det_names = list(metimage.rsr.keys())
            wvl = metimage.rsr[det_names[0]]['wavelength']
            wvl, idx = np.unique(wvl, return_index=True)
            wvl_is_constant = True
            for det in det_names[1:]:
                det_wvl = np.unique(metimage.rsr[det]['wavelength'])
                if not np.alltrue(wvl == det_wvl):
                    LOG.warning(
                        "Wavelngth arrays are not the same among detectors!")
                    wvl_is_constant = False

            if wvl_is_constant:
                arr = wvl
                dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
                dset.attrs['unit'] = 'm'
                dset.attrs['scale'] = 1e-06
                dset[...] = arr

            # Loop over each detector:
            for det in metimage.rsr:
                det_grp = grp.create_group(det)
                wvl = metimage.rsr[det]['wavelength'][
                    ~np.isnan(metimage.rsr[det]['wavelength'])]
                rsp = metimage.rsr[det]['response'][
                    ~np.isnan(metimage.rsr[det]['wavelength'])]
                wvl, idx = np.unique(wvl, return_index=True)
                rsp = np.take(rsp, idx)
                LOG.debug("wvl.shape: %s", str(wvl.shape))
                det_grp.attrs[
                    'central_wavelength'] = get_central_wave(wvl, rsp)
                if not wvl_is_constant:
                    arr = wvl
                    dset = det_grp.create_dataset(
                        'wavelength', arr.shape, dtype='f')
                    dset.attrs['unit'] = 'm'
                    dset.attrs['scale'] = 1e-06
                    dset[...] = arr

                dset = det_grp.create_dataset('response', rsp.shape, dtype='f')
                dset[...] = rsp


def main():
    """Main"""
    for platform_name in ["Metop-SG-A1", ]:
        generate_metimage_file(platform_name)


if __name__ == "__main__":
    main()
