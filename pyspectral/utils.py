#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014-2018 Pytroll

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

"""Utility functions"""

import os
import logging
import tempfile
import numpy as np
from pyspectral.config import get_config

LOG = logging.getLogger(__name__)

WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'

BANDNAMES = {}
BANDNAMES['generic'] = {'VIS006': 'VIS0.6',
                        'VIS008': 'VIS0.8',
                        'IR_016': 'NIR1.6',
                        'IR_039': 'IR3.9',
                        'WV_062': 'IR6.2',
                        'WV_073': 'IR7.3',
                        'IR_087': 'IR8.7',
                        'IR_097': 'IR9.7',
                        'IR_108': 'IR10.8',
                        'IR_120': 'IR12.0',
                        'IR_134': 'IR13.4',
                        'HRV': 'HRV',
                        'I01': 'I1',
                        'I02': 'I2',
                        'I03': 'I3',
                        'I04': 'I4',
                        'I05': 'I5',
                        'M01': 'M1',
                        'M02': 'M2',
                        'M03': 'M3',
                        'M04': 'M4',
                        'M05': 'M5',
                        'M06': 'M6',
                        'M07': 'M7',
                        'M08': 'M8',
                        'M09': 'M9',
                        'C01': 'ch1',
                        'C02': 'ch2',
                        'C03': 'ch3',
                        'C04': 'ch4',
                        'C05': 'ch5',
                        'C06': 'ch6',
                        'C07': 'ch7',
                        'C08': 'ch8',
                        'C09': 'ch9',
                        'C10': 'ch10',
                        'C11': 'ch11',
                        'C12': 'ch12',
                        'C13': 'ch13',
                        'C14': 'ch14',
                        'C15': 'ch15',
                        'C16': 'ch16',
                        }

BANDNAMES['avhrr-3'] = {'3b': 'ch3b',
                        '3a': 'ch3a'}

BANDNAMES['ahi'] = {'B01': 'ch1',
                    'B02': 'ch2',
                    'B03': 'ch3',
                    'B04': 'ch4',
                    'B05': 'ch5',
                    'B06': 'ch6',
                    'B07': 'ch7',
                    'B08': 'ch8',
                    'B09': 'ch9',
                    'B10': 'ch10',
                    'B11': 'ch11',
                    'B12': 'ch12',
                    'B13': 'ch13',
                    'B14': 'ch14',
                    'B15': 'ch15',
                    'B16': 'ch16'
                    }

INSTRUMENTS = {'NOAA-19': 'avhrr/3',
               'NOAA-18': 'avhrr/3',
               'NOAA-17': 'avhrr/3',
               'NOAA-16': 'avhrr/3',
               'NOAA-15': 'avhrr/3',
               'NOAA-14': 'avhrr/2',
               'NOAA-12': 'avhrr/2',
               'NOAA-11': 'avhrr/2',
               'NOAA-9': 'avhrr/2',
               'NOAA-7': 'avhrr/2',
               'NOAA-10': 'avhrr/1',
               'NOAA-8': 'avhrr/1',
               'NOAA-6': 'avhrr/1',
               'TIROS-N': 'avhrr/1',
               'Metop-A': 'avhrr/3',
               'Metop-B': 'avhrr/3',
               'Metop-C': 'avhrr/3',
               'Suomi-NPP': 'viirs',
               'NOAA-20': 'viirs',
               'FY-3D': 'mersi-2',
               'Feng-Yun 3D': 'mersi-2'
               }

HTTP_PYSPECTRAL_RSR = "https://zenodo.org/record/1491277/files/pyspectral_rsr_data.tgz"
RSR_DATA_VERSION_FILENAME = "PYSPECTRAL_RSR_VERSION"
RSR_DATA_VERSION = "v1.0.3"

ATM_CORRECTION_LUT_VERSION = {}
ATM_CORRECTION_LUT_VERSION['antarctic_aerosol'] = {'version': 'v1.0.1',
                                                   'filename': 'PYSPECTRAL_ATM_CORR_LUT_AA'}
ATM_CORRECTION_LUT_VERSION['continental_average_aerosol'] = {'version': 'v1.0.1',
                                                             'filename': 'PYSPECTRAL_ATM_CORR_LUT_CAA'}
ATM_CORRECTION_LUT_VERSION['continental_clean_aerosol'] = {'version': 'v1.0.1',
                                                           'filename': 'PYSPECTRAL_ATM_CORR_LUT_CCA'}
ATM_CORRECTION_LUT_VERSION['continental_polluted_aerosol'] = {'version': 'v1.0.1',
                                                              'filename': 'PYSPECTRAL_ATM_CORR_LUT_CPA'}
ATM_CORRECTION_LUT_VERSION['desert_aerosol'] = {'version': 'v1.0.1',
                                                           'filename': 'PYSPECTRAL_ATM_CORR_LUT_DA'}
ATM_CORRECTION_LUT_VERSION['marine_clean_aerosol'] = {'version': 'v1.0.1',
                                                      'filename': 'PYSPECTRAL_ATM_CORR_LUT_MCA'}
ATM_CORRECTION_LUT_VERSION['marine_polluted_aerosol'] = {'version': 'v1.0.1',
                                                         'filename': 'PYSPECTRAL_ATM_CORR_LUT_MPA'}
ATM_CORRECTION_LUT_VERSION['marine_tropical_aerosol'] = {'version': 'v1.0.1',
                                                         'filename': 'PYSPECTRAL_ATM_CORR_LUT_MTA'}
ATM_CORRECTION_LUT_VERSION['rural_aerosol'] = {'version': 'v1.0.1',
                                               'filename': 'PYSPECTRAL_ATM_CORR_LUT_RA'}
ATM_CORRECTION_LUT_VERSION['urban_aerosol'] = {'version': 'v1.0.1',
                                               'filename': 'PYSPECTRAL_ATM_CORR_LUT_UA'}
ATM_CORRECTION_LUT_VERSION['rayleigh_only'] = {'version': 'v1.0.1',
                                               'filename': 'PYSPECTRAL_ATM_CORR_LUT_RO'}


AEROSOL_TYPES = ['antarctic_aerosol', 'continental_average_aerosol',
                 'continental_clean_aerosol', 'continental_polluted_aerosol',
                 'desert_aerosol', 'marine_clean_aerosol',
                 'marine_polluted_aerosol', 'marine_tropical_aerosol',
                 'rayleigh_only', 'rural_aerosol', 'urban_aerosol']

ATMOSPHERES = {'subarctic summer': 4, 'subarctic winter': 5,
               'midlatitude summer': 6, 'midlatitude winter': 7,
               'tropical': 8, 'us-standard': 9}


HTTPS_RAYLEIGH_LUTS = {}
URL_PREFIX = "https://zenodo.org/record/1288441/files/pyspectral_atm_correction_luts"
for atype in AEROSOL_TYPES:
    name = {'rayleigh_only': 'no_aerosol'}.get(atype, atype)
    url = "{prefix}_{name}.tgz".format(prefix=URL_PREFIX, name=name)
    HTTPS_RAYLEIGH_LUTS[atype] = url


CONF = get_config()
LOCAL_RSR_DIR = CONF.get('rsr_dir')
LOCAL_RAYLEIGH_DIR = CONF.get('rayleigh_dir')

try:
    os.makedirs(LOCAL_RSR_DIR)
except OSError:
    if not os.path.isdir(LOCAL_RSR_DIR):
        raise

RAYLEIGH_LUT_DIRS = {}
for sub_dir_name in HTTPS_RAYLEIGH_LUTS:
    dirname = os.path.join(LOCAL_RAYLEIGH_DIR, sub_dir_name)
    RAYLEIGH_LUT_DIRS[sub_dir_name] = dirname

TB2RAD_DIR = CONF.get('tb2rad_dir', tempfile.gettempdir())


def convert2wavenumber(rsr):
    """
    Take rsr data set with all channels and detectors for an instrument
    each with a set of wavelengths and normalised responses and
    convert to wavenumbers and responses

    :rsr: Relative Spectral Response function (all bands)
    Returns:
      :retv: Relative Spectral Responses in wave number space
      :info: Dictionary with scale (to go convert to SI units) and unit

    """

    retv = {}
    for chname in rsr.keys():  # Go through bands/channels
        retv[chname] = {}
        for det in rsr[chname].keys():  # Go through detectors
            retv[chname][det] = {}
            if 'wavenumber' in rsr[chname][det].keys():
                # Make a copy. Data are already in wave number space
                retv[chname][det] = rsr[chname][det].copy()
                LOG.debug("RSR data already in wavenumber space. No conversion needed.")
                continue

            for sat in rsr[chname][det].keys():
                if sat == "wavelength":
                    # micro meters to cm
                    wnum = 1. / (1e-4 * rsr[chname][det][sat])
                    retv[chname][det]['wavenumber'] = wnum[::-1]
                elif sat == "response":
                    # Flip the response array:
                    if type(rsr[chname][det][sat]) is dict:
                        retv[chname][det][sat] = {}
                        for name in rsr[chname][det][sat].keys():
                            resp = rsr[chname][det][sat][name]
                            retv[chname][det][sat][name] = resp[::-1]
                    else:
                        resp = rsr[chname][det][sat]
                        retv[chname][det][sat] = resp[::-1]

    unit = 'cm-1'
    si_scale = 100.0
    return retv, {'unit': unit, 'si_scale': si_scale}


def get_central_wave(wav, resp, weight=1.0):
    """Calculate the central wavelength or the central wavenumber, depending on
    which parameters is input.  On default the weighting funcion is
    f(lambda)=1.0, but it is possible to add a custom weight, e.g. f(lambda) =
    1./lambda**4 for Rayleigh scattering calculations

    """

    # info: {'unit': unit, 'si_scale': si_scale}
    # To get the wavelenght/wavenumber in SI units (m or m-1):
    # wav = wav * info['si_scale']

    # res = np.trapz(resp*wav, wav) / np.trapz(resp, wav)
    # Check if it is a wavelength or a wavenumber and convert to microns or cm-1:
    # This should perhaps be user defined!?
    # if info['unit'].find('-1') > 0:
    # Wavenumber:
    #     res *=

    return np.trapz(resp * wav * weight, wav) / np.trapz(resp * weight, wav)


def get_bandname_from_wavelength(sensor, wavelength, rsr, epsilon=0.1, multiple_bands=False):
    """Get the bandname from h5 rsr provided the approximate wavelength."""
    # channel_list = [channel for channel in rsr.rsr if abs(
    # rsr.rsr[channel]['det-1']['central_wavelength'] - wavelength) < epsilon]

    chdist_min = 2.0
    chfound = []
    for channel in rsr:
        chdist = abs(
            rsr[channel]['det-1']['central_wavelength'] - wavelength)
        if chdist < chdist_min and chdist < epsilon:
            chfound.append(BANDNAMES.get(sensor, BANDNAMES['generic']).get(channel, channel))

    if len(chfound) == 1:
        return chfound[0]
    elif len(chfound) > 1:
        bstrlist = ['band={}'.format(b) for b in chfound]
        if not multiple_bands:
            raise AttributeError("More than one band found with that wavelength! {}".format(str(bstrlist)))
        else:
            LOG.debug("More than one band found with requested wavelength: %s", str(bstrlist))
        return chfound
    else:
        return None


def sort_data(x_vals, y_vals):
    """Sort the data so that x is monotonically increasing and contains
    no duplicates.
    """
    # Sort data
    idxs = np.argsort(x_vals)
    x_vals = x_vals[idxs]
    y_vals = y_vals[idxs]

    # De-duplicate data
    mask = np.r_[True, (np.diff(x_vals) > 0)]
    if not mask.all():
        # what is this for?
        numof_duplicates = np.repeat(mask, np.equal(mask, False)).shape[0]
        del numof_duplicates
    x_vals = x_vals[mask]
    y_vals = y_vals[mask]

    return x_vals, y_vals


def convert2hdf5(ClassIn, platform_name, bandnames, scale=1e-06):
    """Retrieve original RSR data and convert to internal hdf5 format.

    *scale* is the number which has to be multiplied to the wavelength data in
    order to get it in the SI unit meter

    """
    import h5py

    instr = ClassIn(bandnames[0], platform_name)
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
            sensor = ClassIn(chname, platform_name)
            grp = h5f.create_group(chname)
            wvl = sensor.rsr['wavelength'][~np.isnan(sensor.rsr['wavelength'])]
            rsp = sensor.rsr['response'][~np.isnan(sensor.rsr['wavelength'])]
            grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
            arr = sensor.rsr['wavelength']
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = scale
            dset[...] = arr
            arr = sensor.rsr['response']
            dset = grp.create_dataset('response', arr.shape, dtype='f')
            dset[...] = arr


def download_rsr(**kwargs):
    """Download the pre-compiled hdf5 formatet relative spectral response functions
    from the internet

    """

    #
    import tarfile
    import requests
    TQDM_LOADED = True
    try:
        from tqdm import tqdm
    except ImportError:
        TQDM_LOADED = False

    dest_dir = kwargs.get('dest_dir', LOCAL_RSR_DIR)
    dry_run = kwargs.get('dry_run', False)

    LOG.info("Download RSR files and store in directory %s", dest_dir)

    filename = os.path.join(dest_dir, "pyspectral_rsr_data.tgz")
    LOG.debug("Get data. URL: %s", HTTP_PYSPECTRAL_RSR)
    LOG.debug("Destination = %s", dest_dir)
    if dry_run:
        return

    response = requests.get(HTTP_PYSPECTRAL_RSR)
    if TQDM_LOADED:
        with open(filename, "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)
    else:
        with open(filename, "wb") as handle:
            for data in response.iter_content():
                handle.write(data)

    tar = tarfile.open(filename)
    tar.extractall(dest_dir)
    tar.close()
    os.remove(filename)


def download_luts(**kwargs):
    """Download the luts from internet."""
    #
    import tarfile
    import requests
    TQDM_LOADED = True
    try:
        from tqdm import tqdm
    except ImportError:
        TQDM_LOADED = False

    dry_run = kwargs.get('dry_run', False)

    if 'aerosol_type' in kwargs:
        if isinstance(kwargs['aerosol_type'], (list, tuple, set)):
            aerosol_types = kwargs['aerosol_type']
        else:
            aerosol_types = [kwargs['aerosol_type'], ]
    else:
        aerosol_types = HTTPS_RAYLEIGH_LUTS.keys()

    chunk_size = 10124

    for subname in aerosol_types:

        LOG.debug('Aerosol type: %s', subname)
        http = HTTPS_RAYLEIGH_LUTS[subname]
        LOG.debug('URL = %s', http)

        subdir_path = RAYLEIGH_LUT_DIRS[subname]
        try:
            LOG.debug('Create directory: %s', subdir_path)
            if not dry_run:
                os.makedirs(subdir_path)
        except OSError:
            if not os.path.isdir(subdir_path):
                raise

        if dry_run:
            continue

        response = requests.get(http)
        total_size = int(response.headers['content-length'])

        filename = os.path.join(
            subdir_path, "pyspectral_rayleigh_correction_luts.tgz")
        if TQDM_LOADED:
            with open(filename, "wb") as handle:
                for data in tqdm(iterable=response.iter_content(chunk_size=chunk_size),
                                 total=(total_size / chunk_size), unit='kB'):
                    handle.write(data)
        else:
            with open(filename, "wb") as handle:
                for data in response.iter_content():
                    handle.write(data)

        tar = tarfile.open(filename)
        tar.extractall(subdir_path)
        tar.close()
        os.remove(filename)


def debug_on():
    """Turn debugging logging on.
    """
    logging_on(logging.DEBUG)


_is_logging_on = False


def logging_on(level=logging.WARNING):
    """Turn logging on.
    """
    global _is_logging_on

    if not _is_logging_on:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("[%(levelname)s: %(asctime)s :"
                                               " %(name)s] %(message)s",
                                               '%Y-%m-%d %H:%M:%S'))
        console.setLevel(level)
        logging.getLogger('').addHandler(console)
        _is_logging_on = True

    log = logging.getLogger('')
    log.setLevel(level)
    for h in log.handlers:
        h.setLevel(level)


class NullHandler(logging.Handler):

    """Empty handler"""

    def emit(self, record):
        """Record a message.
        """
        pass


def logging_off():
    """Turn logging off.
    """
    logging.getLogger('').handlers = [NullHandler()]


def get_logger(name):
    """Return logger with null handle
    """

    log = logging.getLogger(name)
    if not log.handlers:
        log.addHandler(NullHandler())
    return log
