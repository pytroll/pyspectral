#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2022 Pytroll developers
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

"""Interface to read original VIIRS relative spectral responses and write to hdf5 file."""

import logging
import os
import sys

import h5py
import numpy as np
from trollsift.parser import compose

from pyspectral.config import get_config
from pyspectral.utils import get_central_wave

LOG = logging.getLogger(__name__)

VIIRS_BAND_NAMES = ['M1', 'M2', 'M3', 'M4', 'M5',
                    'M6', 'M7', 'M8', 'M9', 'M10',
                    'M11', 'M12', 'M13', 'M14', 'M15', 'M16',
                    'I1', 'I2', 'I3', 'I4', 'I5',
                    'DNB']

# JPSS-1:  Band   det  SS      wvl_nm       RSR        SNR   SNR_Thresh QF
# UAID/Swp

DTYPE1 = {'Suomi-NPP': [('bandname', '|S3'),
                        ('detector', '<i4'),
                        ('subsample', '<i4'),
                        ('wavelength', '<f8'),
                        ('band_avg_snr', '<f8'),
                        ('asr', '<f8'),
                        ('response', '<f8'),
                        ('quality_flag', '<i4'),
                        ('xtalk_flag', '<i4')],
          'NOAA-20': [('bandname', '|S3'),
                      ('detector', '<i4'),
                      ('subsample', '<i4'),
                      ('wavelength', '<f8'),
                      ('response', '<f8'),
                      ('snr', '<f8'),
                      ('snr_thresh', '<f8'),
                      ('qf', '<i4'),
                      ('uaid_swp', '<i4')],
          'NOAA-21': [('bandname', '|S3'),
                      ('detector', '<i4'),
                      ('subsample', '<i4'),
                      ('wavelength', '<f8'),
                      ('response', '<f8'),
                      ('snr', '<f8'),
                      ('snr_thresh', '<f8'),
                      ('qf', '<i4'),
                      ('uaid_swp', '<i4')]}


NAMES2 = {'Suomi-NPP': ['bandname',
                        'detector',
                        'subsample',
                        'wavelength',
                        'response'],
          'NOAA-20': []}

DTYPE2 = {'Suomi-NPP': [('bandname', '|S3'),
                        ('detector', '<i4'),
                        ('subsample', '<i4'),
                        ('wavelength', '<f8'),
                        ('response', '<f8')],
          'NOAA-20': []}


#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'


class ViirsRSR(object):
    """Container for the (S-NPP/JPSS) VIIRS RSR data."""

    def __init__(self, bandname, platform_name):
        """Initialize the VIIRS RSR object."""
        self.platform_name = platform_name
        self.bandname = bandname
        self.filename = None
        self.rsr = None

        options = get_config()
        self.output_dir = options.get('rsr_dir', './')

        self.bandfilenames = {}

        self._get_bandfilenames(**options)
        self._get_bandfile(**options)
        LOG.debug("Filename: %s", str(self.filename))
        self._load()

    def _get_bandfilenames(self, **options):
        """Get filename for each band."""
        conf = options[self.platform_name + '-viirs']

        rootdir = conf['rootdir']
        for section in conf:
            if not section.startswith('section'):
                continue
            bandnames = conf[section]['bands']
            for band in bandnames:
                filename = os.path.join(rootdir, conf[section]['filename'])
                self.bandfilenames[band] = compose(
                    filename, {'bandname': band})

    def _get_bandfile(self, **options):
        """Get the VIIRS rsr filename."""
        # Need to understand why there are A&B files for band M16. FIXME!
        # Anyway, the absolute response differences are small, below 0.05

        # LOG.debug("paths = %s", str(self.bandfilenames))

        path = self.bandfilenames[self.bandname]
        if not os.path.exists(path):
            raise IOError("Couldn't find an existing file for this band ({band}): {path}".format(
                band=self.bandname, path=path))

        self.filename = path

    def _load(self, scale=0.001):
        """Load the VIIRS RSR data for the band requested."""
        header_lines_to_skip = get_header_lines2skip(self.filename, self.platform_name)

        try:
            data = np.genfromtxt(self.filename,
                                 skip_header=header_lines_to_skip,
                                 dtype=DTYPE1[self.platform_name])
        except ValueError:
            data = np.genfromtxt(self.filename,
                                 unpack=True, skip_header=header_lines_to_skip,
                                 names=NAMES2[self.platform_name],
                                 dtype=DTYPE2[self.platform_name])

        wavelength = data['wavelength'] * scale
        response = data['response']
        det = data['detector']

        detectors = {}
        for idx in range(int(max(det))):
            detectors["det-{0:d}".format(idx + 1)] = {}
            detectors[
                "det-{0:d}".format(idx + 1)]['wavelength'] = np.repeat(wavelength, np.equal(det, idx + 1))
            detectors[
                "det-{0:d}".format(idx + 1)]['response'] = np.repeat(response, np.equal(det, idx + 1))

        self.rsr = detectors


def get_header_lines2skip(filename, platform_name):
    """Check the file nd find the number of header lines to skip."""
    with open(filename, 'r') as fpt:
        nlines_hd = 0
        line = '% '
        while line.startswith('%'):
            line = fpt.readline()
            nlines_hd = nlines_hd + 1

    return nlines_hd - 1


def create_viirs_rsr(platform_name):
    """Create the VIIRS RSR functions and save to a pyspectral formattet hdf5 file."""
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                                  datefmt=_DEFAULT_TIME_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(handler)

    viirs = ViirsRSR('M1', platform_name)
    filename = os.path.join(viirs.output_dir,
                            "rsr_viirs_{0}.h5".format(platform_name))

    with h5py.File(filename, "w") as h5f:
        h5f.attrs['description'] = 'Relative Spectral Responses for VIIRS'
        h5f.attrs['platform_name'] = platform_name
        h5f.attrs['sensor'] = 'viirs'
        h5f.attrs['band_names'] = VIIRS_BAND_NAMES

        for chname in VIIRS_BAND_NAMES:

            viirs = ViirsRSR(chname, platform_name)
            grp = h5f.create_group(chname)
            grp.attrs['number_of_detectors'] = len(viirs.rsr.keys())
            # Loop over each detector to check if the sampling wavelengths are
            # identical:
            det_names = list(viirs.rsr.keys())
            wvl = viirs.rsr[det_names[0]]['wavelength']
            wvl, idx = np.unique(wvl, return_index=True)
            wvl_is_constant = True
            for det in det_names[1:]:
                det_wvl = np.unique(viirs.rsr[det]['wavelength'])
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
            for det in viirs.rsr:
                det_grp = grp.create_group(det)
                wvl = viirs.rsr[det]['wavelength'][
                    ~np.isnan(viirs.rsr[det]['wavelength'])]
                rsp = viirs.rsr[det]['response'][
                    ~np.isnan(viirs.rsr[det]['wavelength'])]
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


if __name__ == "__main__":
    platform_name = "NOAA-21"
    create_viirs_rsr(platform_name)
