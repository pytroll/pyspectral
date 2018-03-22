#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014-2018 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>
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

"""Reading the spectral responses in the internal pyspectral hdf5 format"""

import os
import numpy as np
from glob import glob
from os.path import expanduser

import logging
LOG = logging.getLogger(__name__)

from pyspectral.config import get_config
from pyspectral.utils import WAVE_NUMBER
from pyspectral.utils import WAVE_LENGTH
from pyspectral.utils import (INSTRUMENTS, download_rsr)
from pyspectral.utils import (RSR_DATA_VERSION_FILENAME, RSR_DATA_VERSION)


class RelativeSpectralResponse(object):

    """Container for the relative spectral response functions for various
    satellite imagers
    """

    def __init__(self, platform_name=None, instrument=None, **kwargs):
        """Create the instance either from platform name and instrument or from
        filename and load the data"""
        self.platform_name = platform_name
        self.instrument = instrument
        self.filename = None
        if not self.instrument or not self.platform_name:
            if 'filename' in kwargs:
                self.filename = kwargs['filename']
            else:
                raise AttributeError(
                    "platform name and sensor or filename must be specified")
        else:
            self._check_instrument()

        self.rsr = {}
        self.description = "Unknown"
        self.band_names = None
        self.unit = '1e-6 m'
        self.si_scale = 1e-6  # How to scale the wavelengths to become SI unit
        self._wavespace = WAVE_LENGTH

        options = get_config()
        self.rsr_dir = options['rsr_dir']
        self.do_download = False
        self._rsr_data_version_uptodate = False

        if 'download_from_internet' in options and options['download_from_internet']:
            self.do_download = True

        if self._get_rsr_data_version() == RSR_DATA_VERSION:
            self._rsr_data_version_uptodate = True

        if not self.filename:
            self._get_filename()

        if not os.path.exists(self.filename) or not os.path.isfile(self.filename):
            errmsg = ('pyspectral RSR file does not exist! Filename = ' +
                      str(self.filename))
            if self.instrument and self.platform_name:
                fmatch = glob(
                    os.path.join(self.rsr_dir, '*{0}*{1}*.h5'.format(self.instrument,
                                                                     self.platform_name)))
                errmsg = (errmsg +
                          '\nFiles matching instrument and satellite platform' +
                          ': ' + str(fmatch))

            raise IOError(errmsg)

        LOG.debug('Filename: %s', str(self.filename))
        self.load()

    def _get_rsr_data_version(self):
        """Check the version of the RSR data from the version file in the RSR
           directory

        """

        rsr_data_version_path = os.path.join(self.rsr_dir, RSR_DATA_VERSION_FILENAME)
        if not os.path.exists(rsr_data_version_path):
            return "v0.0.0"

        with open(rsr_data_version_path, 'r') as fpt:
            # Get the version from the file
            return fpt.readline().strip()

    def _check_instrument(self):
        """Check and try fix instrument name if needed"""
        instr = INSTRUMENTS.get(self.platform_name, self.instrument.lower())
        if instr != self.instrument:
            self.instrument = instr
            LOG.warning("Inconsistent instrument/satellite input - " +
                        "instrument set to %s", self.instrument)

        self.instrument = self.instrument.replace('/', '')

    def _get_filename(self):
        """Get the rsr filname from platform and instrument names, and download if not
           available.

        """
        self.filename = expanduser(
            os.path.join(self.rsr_dir, 'rsr_{0}_{1}.h5'.format(self.instrument,
                                                               self.platform_name)))

        LOG.debug('Filename: %s', str(self.filename))
        if not os.path.exists(self.filename) or not os.path.isfile(self.filename):
            # Try download from the internet!
            LOG.warning("No rsr file %s on disk", self.filename)
            if self.do_download:
                LOG.info("Will download from internet...")
                download_rsr()

        if not self._rsr_data_version_uptodate:
            LOG.warning("rsr data may not be up to date: %s", self.filename)
            if self.do_download:
                LOG.info("Will download from internet...")
                download_rsr()

    def load(self):
        """Read the internally formatet hdf5 relative spectral response data"""
        import h5py

        no_detectors_message = False
        with h5py.File(self.filename, 'r') as h5f:
            self.band_names = [b.decode('utf-8') for b in h5f.attrs['band_names'].tolist()]
            self.description = h5f.attrs['description'].decode('utf-8')
            if not self.platform_name:
                try:
                    self.platform_name = h5f.attrs['platform_name'].decode('utf-8')
                except KeyError:
                    LOG.warning("No platform_name in HDF5 file")
                    try:
                        self.platform_name = h5f.attrs[
                            'platform'] + '-' + h5f.attrs['satnum']
                    except KeyError:
                        LOG.warning(
                            "Unable to determine platform name from HDF5 file content")
                        self.platform_name = None

            if not self.instrument:
                try:
                    self.instrument = h5f.attrs['sensor'].decode('utf-8')
                except KeyError:
                    LOG.warning("No sensor name specified in HDF5 file")
                    self.instrument = INSTRUMENTS.get(self.platform_name)

            for bandname in self.band_names:
                self.rsr[bandname] = {}
                try:
                    num_of_det = h5f[bandname].attrs['number_of_detectors']
                except KeyError:
                    if not no_detectors_message:
                        LOG.debug("No detectors found - assume only one...")
                    num_of_det = 1
                    no_detectors_message = True

                for i in range(1, num_of_det + 1):
                    dname = 'det-{0:d}'.format(i)
                    self.rsr[bandname][dname] = {}
                    try:
                        resp = h5f[bandname][dname]['response'][:]
                    except KeyError:
                        resp = h5f[bandname]['response'][:]

                    self.rsr[bandname][dname]['response'] = resp

                    try:
                        wvl = (h5f[bandname][dname]['wavelength'][:] *
                               h5f[bandname][dname][
                                   'wavelength'].attrs['scale'])
                    except KeyError:
                        wvl = (h5f[bandname]['wavelength'][:] *
                               h5f[bandname]['wavelength'].attrs['scale'])

                    # The wavelength is given in micro meters!
                    self.rsr[bandname][dname]['wavelength'] = wvl * 1e6

                    try:
                        central_wvl = h5f[bandname][
                            dname].attrs['central_wavelength']
                    except KeyError:
                        central_wvl = h5f[bandname].attrs['central_wavelength']

                    self.rsr[bandname][dname][
                        'central_wavelength'] = central_wvl

    def integral(self, bandname):
        """Calculate the integral of the spectral response function for each
        detector.
        """
        intg = {}
        for det in self.rsr[bandname].keys():
            wvl = self.rsr[bandname][det]['wavelength']
            resp = self.rsr[bandname][det]['response']
            intg[det] = np.trapz(resp, wvl)
        return intg

    def convert(self):
        """Convert spectral response functions from wavelength to wavenumber"""

        from pyspectral.utils import (convert2wavenumber, get_central_wave)
        if self._wavespace == WAVE_LENGTH:
            rsr, info = convert2wavenumber(self.rsr)
            for band in rsr.keys():
                for det in rsr[band].keys():
                    self.rsr[band][det][WAVE_NUMBER] = rsr[
                        band][det][WAVE_NUMBER]
                    self.rsr[band][det]['response'] = rsr[
                        band][det]['response']
                    self.unit = info['unit']
                    self.si_scale = info['si_scale']
            self._wavespace = WAVE_NUMBER
            for band in rsr.keys():
                for det in rsr[band].keys():
                    self.rsr[band][det]['central_wavenumber'] = \
                        get_central_wave(self.rsr[band][det][WAVE_NUMBER], self.rsr[band][det]['response'])
                    del self.rsr[band][det][WAVE_LENGTH]
        else:
            errmsg = "Conversion from {wn} to {wl} not supported yet".format(wn=WAVE_NUMBER, wl=WAVE_LENGTH)
            raise NotImplementedError(errmsg)


def main():
    """Main"""
    modis = RelativeSpectralResponse('EOS-Terra', 'modis')
    del(modis)

if __name__ == "__main__":
    main()
