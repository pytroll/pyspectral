"""Reading the spectral responses in the internal pyspectral hdf5 format."""
from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any, TypedDict

import numpy as np
import numpy.typing as npt

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


class RSRResponseDict(TypedDict):
    """Dictionary of Relative Spectral Response information."""

    response: npt.NDArray[np.float32]
    wavelength: npt.NDArray[np.float32]
    central_wavelength: float


class RSRDict(dict):
    """Helper dict-like class to handle multiple names for band keys."""

    def __init__(self, instrument: str):
        """Initialize dict and primary instrument name."""
        self.instrument = instrument
        dict.__init__(self)

    def __getitem__(self, key):
        """Get value either directly or fallback to pre-configured 'standard' names."""
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

    def get(self, key, default=None):
        """Get value either directly or fallback to pre-configured 'standard' names."""
        try:
            return self[key]
        except KeyError:
            return default


class _RSRDataBase:
    """Directory and configuration manager for Relative Spectral Responses (RSR) on disk.

    This class allows interactions with the RSR storage directory without
    having a specific RSR platform/instrument to work with.

    """

    def __init__(self):
        """Initialize the class instance.

        Create the instance either from platform name and instrument or from
        filename and load the data.

        """
        options = get_config()
        self.rsr_dir = Path(options["rsr_dir"]).expanduser()
        self.do_download = options.get("download_from_internet", False)

    @property
    def rsr_data_version(self):
        """Get current version of the RSR directory data."""
        rsr_data_version_path = os.path.join(self.rsr_dir, RSR_DATA_VERSION_FILENAME)
        if not os.path.exists(rsr_data_version_path):
            return "v0.0.0"

        with open(rsr_data_version_path, 'r') as fpt:
            # Get the version from the file
            return fpt.readline().strip()

    @property
    def rsr_data_version_uptodate(self):
        """Determine if the current RSR directory is up to date."""
        return self.rsr_data_version == RSR_DATA_VERSION

    def download_rsr_updates(self, dest_dir: Path | str | None = None, dry_run: bool = False) -> bool:
        """Check RSR directory version and download updates if necessary.

        Args:
            dest_dir: Destination directory for the downloaded tarball before
                extraction.
            dry_run: Whether to actual perform the download and extraction. If True,
                URLs and Paths are logged but not downloaded. If False (default),
                then the download is performed. This is different than the
                'download_from_internet' configuration value as this stops the
                download, but otherwise seems like it occurred.
        Returns: True if the directory was out of date and an update was
            needed (even if 'download_from_internet' configuration value
            disabled the actual update download). False is returned if no
            updated was needed.

        """
        if self.rsr_data_version_uptodate:
            return False

        if not self.do_download:
            LOG.warning("RSR data are old but updates are not downloaded due to 'download_from_internet' setting")
            return True

        LOG.info("Downloading RSR update from internet...")
        download_rsr(dest_dir=dest_dir, dry_run=dry_run)
        return True


class RelativeSpectralResponse(_RSRDataBase):
    """Container for the relative spectral response functions for various satellite imagers."""

    def __init__(
            self,
            platform_name: str | None = None,
            instrument: str | None = None,
            filename: str | Path | None = None,
    ):
        """Initialize the class instance.

        Create the instance either from platform name and instrument or from
        filename, and then load the data from file.

        """
        super(RelativeSpectralResponse, self).__init__()
        filename, platform_name, instrument = self._sanitize_inputs(
            filename,
            platform_name,
            instrument,
        )
        self.filename = filename
        self.platform_name = platform_name
        self.instrument = instrument
        self.unit = '1e-6 m'
        self.si_scale = 1e-6  # How to scale the wavelengths to become SI unit
        self._wavespace = WAVE_LENGTH

        if filename is None:
            # if the user didn't provide a specific file, then make sure we have the most up to date RSRs
            self.download_rsr_updates()

        rsr_info = self._load_rsr_info()
        if self.platform_name is None:
            self.platform_name = rsr_info["platform_name"]
        if self.instrument is None:
            self.instrument = rsr_info["instrument"]
        self.description = rsr_info["description"]
        self.band_names = rsr_info["band_names"]

        self.rsr = RSRDict(self.instrument)
        self.rsr.update(rsr_info["rsr"])

    def _sanitize_inputs(
            self,
            filename: str | Path | None,
            platform_name: str | None,
            instrument: str | None,
    ) -> tuple[Path, str | None, str | None]:
        """Check consistent input concerning platform name, instrument and RSR file name."""
        if filename is not None:
            if instrument is not None or platform_name is not None:
                raise ValueError("'instrument' and 'platform_name' cannot be specified if 'filename' is specified.")

            file_path = Path(filename)
            # platform_name and instrument will be loaded from the file later
        else:
            if instrument is None or platform_name is None:
                raise ValueError("Both 'platform_name' and 'instrument' must be specified if 'filename' is not")

            instrument = check_and_adjust_instrument_name(platform_name, instrument)
            file_path = self.rsr_dir / _get_rsr_filename(platform_name, instrument)
            LOG.debug(f"RSR filename generated from platform_name and instrument: {file_path}")
        return file_path, platform_name, instrument

    def _load_rsr_info(self) -> dict:
        try:
            return _load_rsr_info_from_file(self.filename)
        except FileNotFoundError as e:
            # provide more helpful information if the user didn't provide an explicit filename
            if self.platform_name is not None and self.instrument is not None:
                fmatch = list(self.rsr_dir.glob(f"*{self.instrument}*{self.platform_name}*.h5"))
                errmsg = str(e) + f"\nFiles matching instrument and satellite platform: {fmatch}"
                raise FileNotFoundError(errmsg) from e
            raise

    def integral(self, band_name):
        """Calculate the integral of the spectral response function for each detector."""
        from scipy.integrate import trapezoid

        intg = {}
        for detector_name in self.rsr[band_name].keys():
            wvl = self.rsr[band_name][detector_name]['wavelength']
            resp = self.rsr[band_name][detector_name]['response']
            intg[detector_name] = trapezoid(resp, wvl)
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

    def get_bandname_from_wavelength(self, wavelength, epsilon=0.1, multiple_bands=False):
        """Get the band name from the wavelength."""
        return get_bandname_from_wavelength(self.instrument, wavelength, self.rsr,
                                            epsilon=epsilon, multiple_bands=multiple_bands)


def _load_rsr_info_from_file(filename: Path) -> dict[str, Any]:
    """Read the internally formated HDF5 relative spectral response data."""
    import h5py

    if not filename.is_file():
        raise FileNotFoundError(f"RSR file does not exist! Filename = {filename}")

    with h5py.File(filename, "r") as h5f:
        band_names = [convert2str(x) for x in h5f.attrs['band_names']]
        description = convert2str(h5f.attrs['description'])
        platform_name = _get_platform_name(h5f)
        instrument = _get_instrument(h5f, platform_name)
        rsr = _get_relative_spectral_responses(h5f, band_names)

    return {
        "platform_name": platform_name,
        "instrument": instrument,
        "band_names": band_names,
        "description": description,
        "rsr": rsr,
    }


def _get_platform_name(h5f):
    """Get the platform name."""
    try:
        platform_name = convert2str(h5f.attrs['platform_name'])
    except KeyError:
        LOG.warning("No 'platform_name' in HDF5 file")
        try:
            satname = h5f.attrs['platform']
            satname = convert2str(satname)
            sat_number = h5f.attrs['sat_number']
            platform_name = satname + '-' + str(sat_number)
        except KeyError:
            LOG.warning("Unable to determine platform name from HDF5 file content")
            platform_name = None

    return OSCAR_PLATFORM_NAMES.get(platform_name, platform_name)


def _get_instrument(h5f, platform_name):
    """Get the instrument name."""
    try:
        instrument = convert2str(h5f.attrs['sensor'])
    except KeyError:
        LOG.warning("No sensor name specified in HDF5 file")
        instrument = INSTRUMENTS.get(platform_name)
    return instrument


def _get_relative_spectral_responses(h5f, band_names: list[str]) -> dict[str, dict[str, RSRResponseDict]]:
    """Read the rsr data into a single dictionary."""
    rsr_dict: dict[str, dict[str, RSRResponseDict]] = {}
    for band_name in band_names:
        rsr_dict[band_name] = {}
        for dname in _detector_names(h5f, band_name):
            response = _get_band_responses_per_detector(h5f, band_name, dname)
            wavelength = _get_band_wavelengths_per_detector(h5f, band_name, dname)
            central_wavelength = _get_band_central_wavelength_per_detector(h5f, band_name, dname)
            rsr_dict[band_name][dname] = RSRResponseDict(
                response=response,
                wavelength=wavelength,
                central_wavelength=central_wavelength,
            )
    return rsr_dict


def _detector_names(h5f, band_name: str) -> Iterator[str]:
    num_of_det = _get_number_of_detectors4bandname(h5f, band_name)
    for i in range(1, num_of_det + 1):
        yield 'det-{0:d}'.format(i)


def _get_number_of_detectors4bandname(h5f, band_name: str) -> int:
    """Get the number of detectors (if any) for a specified band."""
    try:
        num_of_det = h5f[band_name].attrs['number_of_detectors']
    except KeyError:
        LOG.debug("No detectors found - assume only one...")
        num_of_det = 1
    return num_of_det


def _get_band_responses_per_detector(h5f, band_name: str, detector_name: str) -> np.ndarray:
    """Get the RSR responses for the band and detector."""
    try:
        resp = h5f[band_name][detector_name]['response'][:]
    except KeyError:
        resp = h5f[band_name]['response'][:]
    return resp


def _get_band_wavelengths_per_detector(h5f, band_name: str, detector_name: str) -> np.ndarray:
    """Get the RSR wavelengths for the band and detector."""
    try:
        wvl = (h5f[band_name][detector_name]['wavelength'][:] *
               h5f[band_name][detector_name]['wavelength'].attrs['scale'])
    except KeyError:
        wvl = (h5f[band_name]['wavelength'][:] *
               h5f[band_name]['wavelength'].attrs['scale'])
    # The wavelength is given in micro meters!
    return wvl * 1e6


def _get_band_central_wavelength_per_detector(h5f, band_name: str, detector_name: str) -> float:
    """Get the central wavelength for the band and detector."""
    try:
        central_wvl = h5f[band_name][detector_name].attrs["central_wavelength"]
    except KeyError:
        central_wvl = h5f[band_name].attrs["central_wavelength"]
    return central_wvl


def _get_rsr_filename(platform_name: str, instrument: str) -> str:
    return f"rsr_{instrument}_{platform_name}.h5"


def check_and_download(dest_dir: str | Path | None = None, dry_run: bool = False) -> None:
    """Do a check for the version and attempt downloading only if needed."""
    rsr = _RSRDataBase()
    if not rsr.download_rsr_updates(dest_dir=dest_dir, dry_run=dry_run):
        LOG.info("RSR data already the latest!")


if __name__ == "__main__":
    modis = RelativeSpectralResponse('EOS-Terra', 'modis')
    del modis
