#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, 2015, 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>
#   Panu Lahtinen <panu.lahtinen@fmi.fi>

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

"""Read the Terra/Aqua MODIS relative spectral response functions."""

import os
import numpy as np

from pyspectral.utils import sort_data
from pyspectral.utils import get_central_wave

import logging
LOG = logging.getLogger(__name__)

from pyspectral import get_config

MODIS_BAND_NAMES = [str(i) for i in range(1, 37)]
SHORTWAVE_BANDS = [str(i) for i in range(1, 20) + [26]]


class ModisRSR(object):

    """Container for the Terra/Aqua RSR data"""

    def __init__(self, bandname, platform_name, sort=True):
        """Init Modis RSR
        """
        self.platform_name = platform_name
        self.bandname = bandname
        self.filenames = {}
        self.requested_band_filename = None
        self.is_sw = False
        if bandname in SHORTWAVE_BANDS:
            self.is_sw = True
        self.scales = {}
        for bname in MODIS_BAND_NAMES:
            self.filenames[bname] = None

        self.rsr = None
        self._sort = sort

        conf = get_config()
        options = {}
        for option, value in conf.items(self.platform_name + '-modis',
                                        raw=True):
            options[option] = value

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')

        self._get_bandfilenames(**options)
        LOG.debug("Filenames: %s", str(self.filenames))
        if os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _get_bandfilenames(self, **options):
        """Get the MODIS rsr filenames"""
        path = options["path"]

        for band in MODIS_BAND_NAMES:
            bnum = int(band)
            LOG.debug("Band = %s", str(band))
            if self.platform_name == 'EOS-Terra':
                filename = os.path.join(path,
                                        "rsr.%d.inb.final" % (bnum))
            else:
                if bnum in [5, 6, 7] + range(20, 37):
                    filename = os.path.join(path, "%.2d.tv.1pct.det" % (bnum))
                else:
                    filename = os.path.join(path, "%.2d.amb.1pct.det" % (bnum))

            self.filenames[band] = filename

    def _load(self):
        """Load the MODIS RSR data for the band requested"""
        if self.is_sw or self.platform_name == 'EOS-Aqua':
            scale = 0.001
        else:
            scale = 1.0
        detector = read_modis_response(self.requested_band_filename, scale)
        self.rsr = detector
        if self._sort:
            self.sort()

    def sort(self):
        """Sort the data so that x is monotonically increasing and contains
        no duplicates.
        """
        if 'wavelength' in self.rsr:
            # Only one detector apparently:
            self.rsr['wavelength'], self.rsr['response'] = \
                sort_data(self.rsr['wavelength'], self.rsr['response'])
        else:
            for detector_name in self.rsr:
                (self.rsr[detector_name]['wavelength'],
                 self.rsr[detector_name]['response']) = \
                    sort_data(self.rsr[detector_name]['wavelength'],
                              self.rsr[detector_name]['response'])


def read_modis_response(filename, scale=1.0):
    """Read the Terra/Aqua MODIS relative spectral responses. Be aware that
    MODIS has several detectors (more than one) compared to e.g. AVHRR which
    has always only one.
    """
    with open(filename, "r") as fid:
        lines = fid.readlines()

    # The IR channels seem to be in microns, whereas the short wave channels are
    # in nanometers! For VIS/NIR scale should be 0.001
    detectors = {}
    for line in lines:
        if line.find("#") == 0:
            continue
        _, det_num, s_1, s_2 = line.split()
        detector_name = 'det-%d' % int(det_num)
        if detector_name not in detectors:
            detectors[detector_name] = {'wavelength': [], 'response': []}

        detectors[detector_name]['wavelength'].append(float(s_1) * scale)
        detectors[detector_name]['response'].append(float(s_2))

    for key in detectors:
        detectors[key]['wavelength'] = np.array(detectors[key]['wavelength'])
        detectors[key]['response'] = np.array(detectors[key]['response'])

    return detectors


def convert2hdf5(platform_name):
    """Retrieve original RSR data and convert to internal hdf5 format"""
    import h5py

    modis = ModisRSR('20', platform_name)
    mfile = os.path.join(modis.output_dir,
                         "rsr_modis_%s.h5" % platform_name)

    with h5py.File(mfile, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for MODIS'
        h5f.attrs['platform_name'] = platform_name
        h5f.attrs['band_names'] = MODIS_BAND_NAMES

        for chname in MODIS_BAND_NAMES:
            modis = ModisRSR(chname, platform_name)
            grp = h5f.create_group(chname)
            grp.attrs['number_of_detectors'] = len(modis.rsr.keys())
            # Loop over each detector to check if the sampling wavelengths are
            # identical:
            det_names = modis.rsr.keys()
            wvl = modis.rsr[det_names[0]]['wavelength']
            wvl_is_constant = True
            for det in det_names[1:]:
                if not np.alltrue(wvl == modis.rsr[det]['wavelength']):
                    wvl_is_constant = False
                    break

            if wvl_is_constant:
                arr = modis.rsr[det_names[0]]['wavelength']
                dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
                dset.attrs['unit'] = 'm'
                dset.attrs['scale'] = 1e-06
                dset[...] = arr

            # Loop over each detector:
            for det in modis.rsr:
                det_grp = grp.create_group(det)
                wvl = modis.rsr[det]['wavelength'][
                    ~np.isnan(modis.rsr[det]['wavelength'])]
                rsp = modis.rsr[det]['response'][
                    ~np.isnan(modis.rsr[det]['wavelength'])]
                det_grp.attrs[
                    'central_wavelength'] = get_central_wave(wvl, rsp)
                if not wvl_is_constant:
                    arr = modis.rsr[det]['wavelength']
                    dset = det_grp.create_dataset(
                        'wavelength', arr.shape, dtype='f')
                    dset.attrs['unit'] = 'm'
                    dset.attrs['scale'] = 1e-06
                    dset[...] = arr

                arr = modis.rsr[det]['response']
                dset = det_grp.create_dataset('response', arr.shape, dtype='f')
                dset[...] = arr


def main():
    """Main"""
    for sat in ['EOS-Terra', 'EOS-Aqua']:
        convert2hdf5(sat)

if __name__ == "__main__":
    main()
