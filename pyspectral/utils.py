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

"""Utility functions."""

import logging
import os
import sys
import tarfile
import warnings
from functools import wraps
from inspect import getfullargspec

import numpy as np
import requests
from scipy.integrate import trapezoid

from pyspectral.bandnames import BANDNAMES
from pyspectral.config import get_config

TQDM_LOADED = True
try:
    from tqdm import tqdm
except ImportError:
    TQDM_LOADED = False


LOG = logging.getLogger(__name__)

WAVE_LENGTH = 'wavelength'
WAVE_NUMBER = 'wavenumber'

INSTRUMENTS = {'Envisat': 'aatsr',
               'GOES-16': 'abi',
               'GOES-17': 'abi',
               'GOES-18': 'abi',
               'GOES-19': 'abi',
               'FY-4A': 'agri',
               'FY-4B': ['agri', 'ghi'],
               'Himawari-8': 'ahi',
               'Himawari-9': 'ahi',
               'GEO-KOMPSAT-2A': 'ami',
               'GEO-KOMPSAT-2B': 'goci-2',
               'NOAA-10': 'avhrr/1',
               'NOAA-6': 'avhrr/1',
               'NOAA-8': 'avhrr/1',
               'TIROS-N': 'avhrr/1',
               'NOAA-11': 'avhrr/2',
               'NOAA-12': 'avhrr/2',
               'NOAA-14': 'avhrr/2',
               'NOAA-7': 'avhrr/2',
               'NOAA-9': 'avhrr/2',
               'Metop-A': 'avhrr/3',
               'Metop-B': 'avhrr/3',
               'Metop-C': 'avhrr/3',
               'NOAA-15': 'avhrr/3',
               'NOAA-16': 'avhrr/3',
               'NOAA-17': 'avhrr/3',
               'NOAA-18': 'avhrr/3',
               'NOAA-19': 'avhrr/3',
               'HY-1C': 'cocts',
               'Meteosat-12': 'fci',
               'MTG-I1': 'fci',
               'Metop-SG-A1': 'metimage',
               'EOS-Aqua': 'modis',
               'EOS-Terra': 'modis',
               'Sentinel-2A': 'msi',
               'Sentinel-2B': 'msi',
               'Sentinel-2C': 'msi',
               'Arctica-M-N1': 'msu-gsa',
               'Electro-L-N2': 'msu-gs',
               'Sentinel-3A': ['olci', 'slstr'],
               'Sentinel-3B': ['olci', 'slstr'],
               'Landsat-8': 'oli_tirs',
               'Landsat-9': 'oli_tirs',
               'Meteosat-10': 'seviri',
               'Meteosat-11': 'seviri',
               'Meteosat-8': 'seviri',
               'Meteosat-9': 'seviri',
               'NOAA-20': 'viirs',
               'NOAA-21': 'viirs',
               'Suomi-NPP': 'viirs',
               'FY-3A': ['virr', 'mersi-1'],
               'FY-3B': ['virr', 'mersi-1'],
               'FY-3C': ['virr', 'mersi-1'],
               'FY-3D': 'mersi-2',
               'FY-3F': 'mersi-3',
               'FY-3G': 'mersi-rm',
               'DSCOVR': 'epic'}


INSTRUMENT_TRANSLATION_DASH2SLASH = {'avhrr-1': 'avhrr/1',
                                     'avhrr-2': 'avhrr/2',
                                     'avhrr-3': 'avhrr/3'}

HTTP_PYSPECTRAL_RSR = "https://zenodo.org/records/14008148/files/pyspectral_rsr_data.tgz"

RSR_DATA_VERSION_FILENAME = "PYSPECTRAL_RSR_VERSION"
RSR_DATA_VERSION = "v1.4.1"


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

#: Aerosol types available as downloadable LUTs for rayleigh correction
AEROSOL_TYPES = ['antarctic_aerosol', 'continental_average_aerosol',
                 'continental_clean_aerosol', 'continental_polluted_aerosol',
                 'desert_aerosol', 'marine_clean_aerosol',
                 'marine_polluted_aerosol', 'marine_tropical_aerosol',
                 'rayleigh_only', 'rural_aerosol', 'urban_aerosol']

ATMOSPHERES = {'subarctic summer': 4, 'subarctic winter': 5,
               'midlatitude summer': 6, 'midlatitude winter': 7,
               'tropical': 8, 'us-standard': 9}

HTTPS_RAYLEIGH_LUTS = {}
LUT_URL_PREFIX = "https://zenodo.org/record/1288441/files/pyspectral_atm_correction_luts"
for atype in AEROSOL_TYPES:
    name = {'rayleigh_only': 'no_aerosol'}.get(atype, atype)
    url = "{prefix}_{name}.tgz".format(prefix=LUT_URL_PREFIX, name=name)
    HTTPS_RAYLEIGH_LUTS[atype] = url


def get_rayleigh_lut_dir(aerosol_type):
    """Get the rayleigh LUT directory for the specified aerosol type."""
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
    return trapezoid(resp * wav * weight, wav) / trapezoid(resp * weight, wav)


def get_bandname_from_wavelength(sensor, wavelength, rsr, epsilon=0.1, multiple_bands=False):
    """Get the bandname from h5 rsr provided the approximate wavelength."""
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


def convert2hdf5(ClassIn, platform_name, bandnames, scale=1e-06, detectors=None):
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

            # If multiple detectors, assume all have same wavelength range in SRF.
            if detectors is not None:
                wvl = sensor.rsr[detectors[0]]['wavelength'][~np.isnan(sensor.rsr[detectors[0]]['wavelength'])]
                arr = sensor.rsr[detectors[0]]['wavelength']
                grp.attrs['number_of_detectors'] = len(detectors)
            else:
                wvl = sensor.rsr['wavelength'][~np.isnan(sensor.rsr['wavelength'])]
                arr = sensor.rsr['wavelength']

            # Save wavelengths to file
            dset = grp.create_dataset('wavelength', arr.shape, dtype='f')
            dset.attrs['unit'] = 'm'
            dset.attrs['scale'] = scale
            dset[...] = arr

            # Now to do the responses
            if detectors is None:
                rsp = sensor.rsr['response'][~np.isnan(sensor.rsr['wavelength'])]
                grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
                arr = sensor.rsr['response']
                dset = grp.create_dataset('response', arr.shape, dtype='f')
                dset[...] = arr
            else:
                for cur_det in detectors:
                    det_grp = grp.create_group(cur_det)
                    rsp = sensor.rsr[cur_det]['response'][~np.isnan(sensor.rsr[cur_det]['wavelength'])]
                    det_grp.attrs['central_wavelength'] = get_central_wave(wvl, rsp)
                    arr = sensor.rsr[cur_det]['response']
                    dset = det_grp.create_dataset('response', arr.shape, dtype='f')
                    dset[...] = arr


def download_rsr(dest_dir=None, dry_run=False):
    """Download the relative spectral response functions.

    Download the pre-compiled HDF5 formatted relative spectral response
    functions from the internet as tarballs, extracts them, then deletes
    the tarball.

    See :func:`pyspectral.rsr_reader.check_and_download` for a "smart" version
    of this process that only downloads the necessary files.

    Args:
        dest_dir (str): Path to put the temporary tarball and extracted RSR
            files.
        dry_run (bool): If True, don't actually download files, only log what
            URLs would be downloaded. Defaults to False.

    """
    config = get_config()
    local_rsr_dir = config.get('rsr_dir')
    dest_dir = dest_dir or local_rsr_dir

    LOG.info("Download RSR files and store in directory %s", dest_dir)
    filename = os.path.join(dest_dir, "pyspectral_rsr_data.tgz")
    LOG.debug("RSR URL: %s", HTTP_PYSPECTRAL_RSR)
    LOG.debug("Destination = %s", dest_dir)
    if dry_run:
        return

    _download_tarball_and_extract(HTTP_PYSPECTRAL_RSR, filename, dest_dir)


def download_luts(aerosol_types=None, dry_run=False, aerosol_type=None):
    """Download the luts from internet.

    See :func:`pyspectral.rayleigh.check_and_download` for a "smart" version
    of this process that only downloads the necessary files.

    Args:
        aerosol_types (Iterable): Aerosol types to download the LUTs for.
            Defaults to all aerosol types. See :data:`AEROSOL_TYPES` for the
            full list.
        dry_run (bool): If True, don't actually download files, only log what
            URLs would be downloaded. Defaults to False.
        aerosol_type (str): Deprecated.

    """
    aerosol_types = _get_aerosol_types(aerosol_types, aerosol_type)
    for subname in aerosol_types:
        LOG.debug('Aerosol type: %s', subname)
        lut_tarball_url = HTTPS_RAYLEIGH_LUTS[subname]
        LOG.debug('Atmospheric LUT URL = %s', lut_tarball_url)

        subdir_path = get_rayleigh_lut_dir(subname)
        LOG.debug('Create directory: %s', subdir_path)
        if not dry_run:
            os.makedirs(subdir_path, exist_ok=True)
        if dry_run:
            continue

        local_tarball_pathname = os.path.join(subdir_path, "pyspectral_rayleigh_correction_luts.tgz")
        _download_tarball_and_extract(lut_tarball_url, local_tarball_pathname, subdir_path)


def _get_aerosol_types(aerosol_types, aerosol_type):
    if aerosol_type is not None:
        warnings.warn("'aerosol_type' is deprecated, use 'aerosol_types' instead.", UserWarning,
                      stacklevel=3)
        if isinstance(aerosol_type, (list, tuple, set)):
            aerosol_types = aerosol_type
        else:
            aerosol_types = [aerosol_type]
    elif aerosol_types is None:
        aerosol_types = list(HTTPS_RAYLEIGH_LUTS.keys())
    return aerosol_types


def _download_tarball_and_extract(tarball_url, local_pathname, extract_dir):
    chunk_size = 1024 * 1024  # 1 MB
    response = requests.get(tarball_url)
    total_size = int(response.headers['content-length'])

    with open(local_pathname, "wb") as handle:
        for data in _tqdm_or_iter(response.iter_content(chunk_size=chunk_size),
                                  total=(int(total_size / chunk_size + 0.5)),
                                  unit='kB'):
            handle.write(data)

    tar = tarfile.open(local_pathname)
    tar_kwargs = {} if sys.version_info < (3, 12) else {"filter": "data"}
    tar.extractall(extract_dir, **tar_kwargs)
    tar.close()
    os.remove(local_pathname)


def _tqdm_or_iter(an_iterable, **tqdm_kwargs):
    """Wrap an iterable with tqdm if it is available, otherwise return the iterable."""
    if TQDM_LOADED:
        return tqdm(iterable=an_iterable, **tqdm_kwargs)
    else:
        return an_iterable


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
    """Convert an ``numpy.bytes_`` to str.

    Note: ``numpy.string_`` was deprecated in numpy 2.0 in favor of
    ``numpy.bytes_``.

    Args:
        value (ndarray): scalar or 1-element numpy array to convert
    Raises:
        ValueError: if value is array larger than 1-element or it is not of
                    type `numpy.bytes_` or it is not a numpy array

    """
    if isinstance(value, str):
        return value

    if hasattr(value, 'dtype') and \
            issubclass(value.dtype.type, (np.str_, np.bytes_, np.object_)) \
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


def _replace_inst_name(instruments):
    """Replace an instrument name if it's not available on a platform."""
    if isinstance(instruments, list):
        return instruments[0]
    else:
        return instruments


def check_and_adjust_instrument_name(platform_name, instrument):
    """Check instrument name and try fix if inconsistent.

    It checks against the possible listed instrument names for each platform.
    It also makes an adjustment replacing names like avhrr/1 with avhrr1,
    removing the '/'.
    """
    instr = INSTRUMENTS.get(platform_name, instrument.lower())
    if isinstance(instr, list):
        for inst in instr:
            goodinst = are_instruments_identical(inst, instrument.lower())
            if goodinst:
                break
    else:
        goodinst = are_instruments_identical(instr, instrument.lower())

    if not goodinst:
        instrument = _replace_inst_name(instr)
        LOG.warning("Inconsistent instrument/satellite input - instrument set to %s",
                    instrument)

    return instrument.lower().replace('/', '').replace('-', '')


def are_instruments_identical(name1, name2):
    """Given two instrument names check if they are both describing the same instrument.

    Takes care of the case of AVHRR where the internal pyspectral naming
    (following WMO Oscar) is is with a slash as in 'avhrr/1', but where a
    naming using a dash instead is equally accepted, as in 'avhrr-1'.
    """
    if not isinstance(name1, str) or not isinstance(name2, str):
        raise ValueError("Instrument names must be strings.")

    if name1 == name2:
        return True
    if name1 == INSTRUMENT_TRANSLATION_DASH2SLASH.get(name2):
        return True
    return False


def use_map_blocks_on(argument_to_run_map_blocks_on):
    """Use map blocks on a given argument.

    This decorator assumes only one of the arguments of the decorated function is chunked.
    """
    def decorator(f):
        argspec = getfullargspec(f)
        argument_index = argspec.args.index(argument_to_run_map_blocks_on)

        @wraps(f)
        def wrapper(*args, **kwargs):
            array = args[argument_index]
            chunks = getattr(array, "chunks", None)
            if chunks is None:
                return f(*args, **kwargs)
            import dask.array as da
            import xarray as xr
            if isinstance(array, da.Array):
                return da.map_blocks(f, *args, **kwargs)
            elif isinstance(array, xr.DataArray):
                new_array = array.copy()
                new_args = list(args)
                new_args[argument_index] = array.data
                new_data = da.map_blocks(f, *new_args, **kwargs)
                new_array.data = new_data
                return new_array
            else:
                raise NotImplementedError(f"Don't know how to map_blocks on {type(array)}")
        return wrapper
    return decorator
