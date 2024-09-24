#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2024 Pytroll developers
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

"""Reading the spectral responses in the internal pyspectral hdf5 format."""

import logging
import os
from glob import glob
from os.path import expanduser

from scipy.integrate import trapezoid

from pyspectral.bandnames import BANDNAMES
from pyspectral.config import get_config
from pyspectral.utils import (
    INSTRUMENTS,
    RSR_DATA_VERSION,
    RSR_DATA_VERSION_FILENAME,
    WAVE_LENGTH,
    WAVE_NUMBER,
    check_and_adjust_instrument_name,
    convert2str,
    convert2wavenumber,
    download_rsr,
    get_bandname_from_wavelength,
    get_central_wave,
)

LOG = logging.getLogger(__name__)

OSCAR_PLATFORM_NAMES = {'eos-2': 'EOS-Aqua',
                        'meteosat-11': 'Meteosat-11',
                        'meteosat-10': 'Meteosat-10',
                        'meteosat-9': 'Meteosat-9',
                        'meteosat-8': 'Meteosat-8'}


class RSRDict(dict):
    """Helper dict-like class to handle multiple names for band keys."""

    def __init__(self, instrument=None):
        """Initialize dict and primary instrument name."""
        self.instrument = instrument
        dict.__init__(self)

    def __getitem__(self, key):
        """Get value either directly or fallback to pre-configured 'standard' names.."""
        try:
            val = dict.__getitem__(self, key)
        except KeyError:
            if self.instrument in BANDNAMES and key in BANDNAMES[self.instrument]:
                val = dict.__getitem__(self, BANDNAMES[self.instrument][key])
            elif key in BANDNAMES['generic']:
                val = dict.__getitem__(self, BANDNAMES['generic'][key])
            else:
                raise KeyError(f'Band not found in RSR for {self.instrument}: {key}')
        return val


class RSRDataBaseClass(object):
    """Data container for the Relative Spectral Responses for all (supported) satellite sensors."""

    def __init__(self):
        """Initialize the class instance.

        Create the instance either from platform name and instrument or from
        filename and load the data.

        """
        self.rsr = RSRDict()
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

    def _get_rsr_data_version(self):
        """Check the version of the RSR data from the version file in the RSR directory."""
        rsr_data_version_path = os.path.join(self.rsr_dir, RSR_DATA_VERSION_FILENAME)
        if not os.path.exists(rsr_data_version_path):
            return "v0.0.0"

        with open(rsr_data_version_path, 'r') as fpt:
            # Get the version from the file
            return fpt.readline().strip()

    @property
    def rsr_data_version_uptodate(self):
        """Check whether RSR data are up to date."""
        return self._rsr_data_version_uptodate


class RelativeSpectralResponse(RSRDataBaseClass):
    """Container for the relative spectral response functions for various satellite imagers."""

    def __init__(self, platform_name=None, instrument=None, filename=None):
        """Initialize the class instance.

        Create the instance either from platform name and instrument or from
        filename, and then load the data from file.

        """
        super(RelativeSpectralResponse, self).__init__()

        self.platform_name = platform_name
        self.instrument = instrument
        self.filename = filename

        self._check_consistent_input()

        self.load()
        self.rsr.instrument = self.instrument

    def _check_consistent_input(self):
        """Check consistent input concerning platform name, instrument and RSR file name."""
        if not self.filename:
            if not self.instrument or not self.platform_name:
                raise AttributeError(
                    "Either platform name and sensor, or filename, must be specified")

            self._check_instrument()
            self._get_filename()

        self._check_filename_exist()

    def _check_instrument(self):
        """Check and try fix instrument name if needed."""
        self.instrument = check_and_adjust_instrument_name(self.platform_name, self.instrument)

    def _get_filename(self):
        """Get the rsr filname from platform and instrument names, and download if not available."""
        self.filename = expanduser(
            os.path.join(self.rsr_dir, 'rsr_{0}_{1}.h5'.format(self.instrument,
                                                               self.platform_name)))

        LOG.debug('Filename: %s', str(self.filename))
        if not os.path.exists(self.filename) or not os.path.isfile(self.filename):
            LOG.warning("No rsr file %s on disk", self.filename)

            if self._rsr_data_version_uptodate:
                LOG.info("RSR data up to date, so seems there is no support for this platform and sensor")
            else:
                # Try download from the internet!
                if self.do_download:
                    LOG.info("Will download from internet...")
                    download_rsr()
                    if self._get_rsr_data_version() == RSR_DATA_VERSION:
                        self._rsr_data_version_uptodate = True

        if not self._rsr_data_version_uptodate:
            LOG.warning("rsr data may not be up to date: %s", self.filename)
            if self.do_download:
                LOG.info("Will download from internet...")
                download_rsr()

    def _check_filename_exist(self):
        """Check that the file exist."""
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

    def load(self):
        """Read the internally formatet hdf5 relative spectral response data."""
        import h5py

        with h5py.File(self.filename, 'r') as h5f:
            self.set_band_names(h5f)
            self.set_description(h5f)
            self.set_platform_name(h5f)
            self.set_instrument(h5f)
            self.get_relative_spectral_responses(h5f)

    def integral(self, bandname):
        """Calculate the integral of the spectral response function for each detector."""
        intg = {}
        for det in self.rsr[bandname].keys():
            wvl = self.rsr[bandname][det]['wavelength']
            resp = self.rsr[bandname][det]['response']
            intg[det] = trapezoid(resp, wvl)
        return intg

    def convert(self):
        """Convert spectral response functions from wavelength to wavenumber."""
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

    def set_description(self, h5f):
        """Set the description."""
        self.description = h5f.attrs['description']
        self.description = convert2str(self.description)

    def set_band_names(self, h5f):
        """Set the band names."""
        self.band_names = h5f.attrs['band_names']
        self.band_names = [convert2str(x) for x in self.band_names]

    def set_instrument(self, h5f):
        """Set the instrument name."""
        if self.instrument:
            return

        try:
            self.instrument = h5f.attrs['sensor']
            self.instrument = convert2str(self.instrument)
        except KeyError:
            LOG.warning("No sensor name specified in HDF5 file")
            self.instrument = INSTRUMENTS.get(self.platform_name)

    def set_platform_name(self, h5f):
        """Set the platform name."""
        if self.platform_name:
            return

        try:
            self.platform_name = h5f.attrs['platform_name']
            self.platform_name = convert2str(self.platform_name)
        except KeyError:
            LOG.warning("No platform_name in HDF5 file")
            try:
                satname = h5f.attrs['platform']
                satname = convert2str(satname)
                sat_number = h5f.attrs['sat_number']
                self.platform_name = satname + '-' + str(sat_number)
            except KeyError:
                LOG.warning(
                    "Unable to determine platform name from HDF5 file content")
                self.platform_name = None

        self.platform_name = OSCAR_PLATFORM_NAMES.get(self.platform_name, self.platform_name)

    def get_number_of_detectors4bandname(self, h5f, bandname):
        """For a band name get the number of detectors, if any."""
        try:
            num_of_det = h5f[bandname].attrs['number_of_detectors']
        except KeyError:
            LOG.debug("No detectors found - assume only one...")
            num_of_det = 1

        return num_of_det

    def set_band_responses_per_detector(self, h5f, bandname, detector_name):
        """Set the RSR responses for the band and detector."""
        self.rsr[bandname][detector_name] = {}
        try:
            resp = h5f[bandname][detector_name]['response'][:]
        except KeyError:
            resp = h5f[bandname]['response'][:]

        self.rsr[bandname][detector_name]['response'] = resp

    def set_band_wavelengths_per_detector(self, h5f, bandname, detector_name):
        """Set the RSR wavelengths for the band and detector."""
        try:
            wvl = (h5f[bandname][detector_name]['wavelength'][:] *
                   h5f[bandname][detector_name]['wavelength'].attrs['scale'])
        except KeyError:
            wvl = (h5f[bandname]['wavelength'][:] *
                   h5f[bandname]['wavelength'].attrs['scale'])

        # The wavelength is given in micro meters!
        self.rsr[bandname][detector_name]['wavelength'] = wvl * 1e6

    def set_band_central_wavelength_per_detector(self, h5f, bandname, detector_name):
        """Set the central wavelength for the band and detector."""
        try:
            central_wvl = h5f[bandname][detector_name].attrs['central_wavelength']
        except KeyError:
            central_wvl = h5f[bandname].attrs['central_wavelength']

        self.rsr[bandname][detector_name]['central_wavelength'] = central_wvl

    def get_relative_spectral_responses(self, h5f):
        """Read the rsr data and add to the object."""
        for bandname in self.band_names:
            self.rsr[bandname] = {}

            num_of_det = self.get_number_of_detectors4bandname(h5f, bandname)
            for i in range(1, num_of_det + 1):
                dname = 'det-{0:d}'.format(i)
                self.set_band_responses_per_detector(h5f, bandname, dname)
                self.set_band_wavelengths_per_detector(h5f, bandname, dname)
                self.set_band_central_wavelength_per_detector(h5f, bandname, dname)

    def get_bandname_from_wavelength(self, wavelength, epsilon=0.1, multiple_bands=False):
        """Get the band name from the wavelength."""
        return get_bandname_from_wavelength(self.instrument, wavelength, self.rsr,
                                            epsilon=epsilon, multiple_bands=multiple_bands)


def check_and_download(dest_dir=None, dry_run=False):
    """Do a check for the version and attempt downloading only if needed."""
    rsr = RSRDataBaseClass()
    if rsr.rsr_data_version_uptodate:
        LOG.info("RSR data already the latest!")
    else:
        download_rsr(dest_dir=dest_dir, dry_run=dry_run)


if __name__ == "__main__":
    modis = RelativeSpectralResponse('EOS-Terra', 'modis')
    del modis
