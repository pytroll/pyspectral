#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2022 Pytroll developers
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

"""Utility functions."""

import os
import logging
import numpy as np
from pyspectral.config import get_config
from pyspectral.bandnames import BANDNAMES

LOG = logging.getLogger(__name__)

WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'


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
               'EOS-Aqua': 'modis',
               'EOS-Terra': 'modis',
               'FY-3D': 'mersi-2',
               'FY-3C': 'virr',
               'FY-3B': 'virr',
               'Feng-Yun 3D': 'mersi-2',
               'Meteosat-11': 'seviri',
               'Meteosat-10': 'seviri',
               'Meteosat-9': 'seviri',
               'Meteosat-8': 'seviri',
               'FY-4A': 'agri',
               'GEO-KOMPSAT-2A': 'ami',
               'MTG-I1': 'fci'
               }

HTTP_PYSPECTRAL_RSR = "https://zenodo.org/record/6026563/files/pyspectral_rsr_data.tgz"

RSR_DATA_VERSION_FILENAME = "PYSPECTRAL_RSR_VERSION"
RSR_DATA_VERSION = "v1.0.18"

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


def get_rayleigh_lut_dir(aerosol_type):
    """Get the rayleight LUT directory for the specified aerosol type."""
    conf = get_config()
    local_rayleigh_dir = conf.get('rayleigh_dir')
    return os.path.join(local_rayleigh_dir, aerosol_type)


def convert2wavenumber(rsr):
    """Convert Spectral Responses from wavelength to wavenumber space.

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
                    if isinstance(rsr[chname][det][sat], dict):
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
    """Calculate the central wavelength or the central wavenumber.

    Calculate the central wavelength or the central wavenumber, depending on
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
    if len(chfound) > 1:
        bstrlist = ['band={}'.format(b) for b in chfound]
        if not multiple_bands:
            raise AttributeError("More than one band found with that wavelength! {}".format(str(bstrlist)))
        LOG.debug("More than one band found with requested wavelength: %s", str(bstrlist))
        return chfound
    return None


def sort_data(x_vals, y_vals):
    """Sort the data so that x is monotonically increasing and contains no duplicates."""
    # Sort data
    # (This is needed in particular for EOS-Terra responses, as there are duplicates)
    idxs = np.argsort(x_vals)
    x_vals = x_vals[idxs]
    y_vals = y_vals[idxs]

    # De-duplicate data
    mask = np.r_[True, (np.diff(x_vals) > 0)]
    if not mask.all():
        numof_duplicates = np.repeat(mask, np.equal(mask, False)).shape[0]
        LOG.debug("Number of duplicates in the response function: %d - removing them",
                  numof_duplicates)
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
    """Download the relative spectral response functions.

    Download the pre-compiled hdf5 formatet relative spectral response functions
    from the internet

    """
    import tarfile
    import requests
    TQDM_LOADED = True
    try:
        from tqdm import tqdm
    except ImportError:
        TQDM_LOADED = False

    config = get_config()
    local_rsr_dir = config.get('rsr_dir')
    dest_dir = kwargs.get('dest_dir', local_rsr_dir)
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

    chunk_size = 1024 * 1024  # 1 MB
    for subname in aerosol_types:

        LOG.debug('Aerosol type: %s', subname)
        http = HTTPS_RAYLEIGH_LUTS[subname]
        LOG.debug('URL = %s', http)

        subdir_path = get_rayleigh_lut_dir(subname)
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
                                 total=(int(total_size / chunk_size + 0.5)), unit='kB'):
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
    """Turn debugging logging on."""
    logging_on(logging.DEBUG)


_is_logging_on = False


def logging_on(level=logging.WARNING):
    """Turn logging on."""
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
    """Empty handler."""

    def emit(self, record):
        """Record a message."""


def logging_off():
    """Turn logging off."""
    logging.getLogger('').handlers = [NullHandler()]


def get_logger(name):
    """Return logger with null handle."""
    log = logging.getLogger(name)
    if not log.handlers:
        log.addHandler(NullHandler())
    return log


def get_wave_range(in_chan, threshold=0.15):
    """Return central, min and max wavelength in an RSR greater than threshold.

    An RSR function will generally start near zero, increase to a maximum and
    then drop back to near zero. This function takes advantage of this to find
    the first and last points where the RSR is greater than a threshold. These
    points are then defined as the minimum and maximum wavelengths for a
    given channel, and can be used, for example, in Satpy reader YAML files.

    """
    cwl = get_central_wave(in_chan['wavelength'], in_chan['response'])

    wvls = in_chan['wavelength']
    rsr = in_chan['response']

    pts = (rsr > threshold).nonzero()
    min_wvl = wvls[pts[0][0]]
    max_wvl = wvls[pts[0][-1]]

    return [min_wvl, cwl, max_wvl]


def convert2str(value):
    """Convert a value to string.

    Args:
        value: Either a str, bytes or 1-element numpy array

    """
    value = bytes2string(value)
    return np2str(value)


def np2str(value):
    """Convert an `numpy.string_` to str.

    Args:
        value (ndarray): scalar or 1-element numpy array to convert
    Raises:
        ValueError: if value is array larger than 1-element or it is not of
                    type `numpy.string_` or it is not a numpy array

    """
    if isinstance(value, str):
        return value

    if hasattr(value, 'dtype') and \
            issubclass(value.dtype.type, (np.str_, np.string_, np.object_)) \
            and value.size == 1:
        value = value.item()
        # python 3 - was scalar numpy array of bytes
        # otherwise python 2 - scalar numpy array of 'str'
        if not isinstance(value, str):
            return value.decode()
        return value

    raise ValueError("Array is not a string type or is larger than 1")


def bytes2string(var):
    """Decode a bytes variable and return a string."""
    if isinstance(var, bytes):
        return var.decode('utf-8')
    return var
