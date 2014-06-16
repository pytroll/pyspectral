#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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

"""Read the Terra/Aqua MODIS relative spectral response functions.
"""

import logging
LOG = logging.getLogger(__name__)

import ConfigParser
import os
import numpy as np

from pyspectral.utils import sort_data
from pyspectral.utils import get_central_wave

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")

MODIS_BAND_NAMES = [str(i) for i in range(1, 37)]
SATELLITE_NAME = {'terra': 'eos1', 'aqua': 'eos2'}
PLATFORM_NAME = {'terra': 'eos', 'aqua': 'eos'}
SATELLITE_NUMBER = {'terra': 1, 'aqua': 2}
SHORTWAVE_BANDS = [str(i) for i in range(1, 20) + [26]]


class ModisRSR(object):

    """Container for the Terra/Aqua RSR data"""

    def __init__(self, bandname, satname, sort=True):
        """
        """
        self.satname = satname
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
        conf = ConfigParser.ConfigParser()
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.exception(
                'Failed reading configuration file: ' + str(CONFIG_FILE))
            raise

        options = {}
        for option, value in conf.items(self.satname + '-modis', raw=True):
            options[option] = value

        for option, value in conf.items('general', raw=True):
            options[option] = value

        self.output_dir = options.get('rsr_dir', './')

        self._get_bandfilenames(**options)
        LOG.debug("Filenames: " + str(self.filenames))
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
            LOG.debug("Band= " + str(band))
            if self.satname == 'terra':
                filename = os.path.join(path,
                                        "rsr.%d.oobd.det" % (bnum))
            else:
                if bnum in [5, 6, 7] + range(20, 37):
                    filename = os.path.join(path, "%.2d.tv.1pct.det" % (bnum))
                else:
                    filename = os.path.join(path, "%.2d.amb.1pct.det" % (bnum))

            self.filenames[band] = filename

    def _load(self):
        """Load the MODIS RSR data for the band requested
        """

        if self.is_sw or self.satname == 'aqua':
            scale = 0.001
        else:
            scale = 1.0
        detector = read_modis_response(self.requested_band_filename, scale)
        self.rsr = detector
        if self._sort:
            self.sort()

    def sort(self):
        """Sort the data so that x is monotonically increasing and contains
        no duplicates."""
        if 'wavelength' in self.rsr:
            # Only one detector apparently:
            self.rsr['wavelength'], self.rsr['response'] = \
                sort_data(self.rsr['wavelength'], self.rsr['response'])
        else:
            for detector_name in self.rsr:
                self.rsr[detector_name]['wavelength'], self.rsr[detector_name]['response'] = \
                    sort_data(
                        self.rsr[detector_name]['wavelength'], self.rsr[detector_name]['response'])


def read_modis_response(filename, scale=1.0):
    """Read the Terra/Aqua MODIS relative spectral responses. Be aware that
    MODIS has several detectors (more than one) compared to e.g. AVHRR which
    has always only one.
    """
    fd = open(filename, "r")
    lines = fd.readlines()
    fd.close()

    # The IR channels seem to be in microns, whereas the short wave channels are
    # in nanometers! For VIS/NIR scale should be 0.001
    detectors = {}
    for line in lines:
        if line.find("#") == 0:
            continue
        dummy1, dummy2, s1, s2 = line.split()
        detector_name = 'det-%d' % int(dummy2)
        if detector_name not in detectors:
            detectors[detector_name] = {'wavelength': [], 'response': []}

        detectors[detector_name]['wavelength'].append(float(s1) * scale)
        detectors[detector_name]['response'].append(float(s2))

    for key in detectors:
        detectors[key]['wavelength'] = np.array(detectors[key]['wavelength'])
        detectors[key]['response'] = np.array(detectors[key]['response'])

    return detectors


def convert2hdf5(platform):
    """Retrieve original RSR data and convert to internal hdf5 format"""
    import h5py

    modis = ModisRSR('20', platform)
    mfile = os.path.join(modis.output_dir,
                         "rsr_modis_%s.h5" % SATELLITE_NAME.get(platform, platform))

    with h5py.File(mfile, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for MODIS'
        h5f.attrs['platform'] = PLATFORM_NAME.get(platform, platform)
        h5f.attrs['sat_number'] = SATELLITE_NUMBER.get(platform, 'unknown')
        h5f.attrs['band_names'] = MODIS_BAND_NAMES

        for chname in MODIS_BAND_NAMES:
            modis = ModisRSR(chname, platform)
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


if __name__ == "__main__":

    for sat in ['terra', 'aqua']:
        convert2hdf5(sat)
