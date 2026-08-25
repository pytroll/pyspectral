"""Read the MetImage relative spectral response functions.

Data from EUMETSAT. Acquired under export control on May 7, 2026

These are the full resolution SRFs per detector.
"""

import logging
import os
from pathlib import Path

import h5py
import numpy as np

from pyspectral.bandnames import BANDNAMES
from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import get_central_wave

LOG = logging.getLogger(__name__)


METIMAGE_BAND_NAMES_DICT = {BANDNAMES['VII'][k]: k for k in BANDNAMES['VII']}
METIMAGE_BAND_NAMES = list(METIMAGE_BAND_NAMES_DICT.keys())

METIMAGE_BAND_NAMES_DICT_REVERSE = {v: k for k, v in METIMAGE_BAND_NAMES_DICT.items()}

VISNIR = "VISNIR"
SMWIR = "SMWIR"
VLWIR = "VLWIR"

CHANNEL_GROUP_START_NUM = {VISNIR: 0, SMWIR: 7, VLWIR: 14}


class ISRFReader:
    """Reader for the original EUMETSAT METimage SRF data."""

    def __init__(self, filename):
        """Initialize the class."""
        self.filename = Path(filename)
        self._h5 = None

    def __enter__(self):
        """Instantiate the class, creating the hdf5 file object."""
        self._h5 = h5py.File(self.filename, "r")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the class."""
        self.close()

    def close(self):
        """Close the object, making sure to close the hdf5 file object."""
        if self._h5 is not None:
            self._h5.close()
            self._h5 = None

    def band_groups(self):
        """Get the three band/band-group names in the hdf5 file."""
        return ["VISNIR", "SMWIR", "VLWIR"]

    def wavelength(self, band, start=None, stop=None):
        """Get the wavelength array."""
        dset = self._h5[f"{band}_Wavelength"]
        return dset[start:stop, 0]

    def isrf(self, band, detector=None, channel=None, wl_slice=None):
        """
        Return ISRF data lazily sliced from file.

        Dimensions:
            wavelength, detector, channel

        Parameters
        ----------
        band : str
            "VISNIR", "SMWIR", or "VLWIR"
        detector : int or None
            Detector index, 0..23. If None, return all detectors.
        channel : int or None
            Channel index. If None, return all channels.
        wl_slice : slice
            Wavelength/sample slice.
        """
        dset = self._h5[f"{band}_ISRF"]

        det_sel = slice(None) if detector is None else detector
        ch_sel = slice(None) if channel is None else channel

        if not wl_slice:
            wl_slice = slice(None)

        return dset[wl_slice, det_sel, ch_sel]

    def shape(self, band):
        """Get the shape of the band group dataset from the hdf5 object."""
        return self._h5[f"{band}_ISRF"].shape


def get_groupname_from_bandname(band):
    """Get band group name in hdf5 file from band (channel) name."""
    groupname = "VLWIR"
    wv = int(band.split("_")[-1])
    if wv > 6000:
        groupname = "VLWIR"
    elif wv > 1000:
        groupname = "SMWIR"
    else:
        groupname = "VISNIR"
    return groupname


class MetImageRSR(InstrumentRSR):
    """Container for the EPS-SG MetImage RSR data."""

    def __init__(self, bandname, platform_name):
        """Initialize the class."""
        super(MetImageRSR, self).__init__(
            bandname, platform_name, list(METIMAGE_BAND_NAMES))

        self.instrument = 'metimage'
        self._get_options_from_config()

        LOG.debug(f'Filename: {str(self.path)}')
        if self.path.exists():
            self.requested_band_filename = self.path
            self.nc_band_name = METIMAGE_BAND_NAMES_DICT[bandname]
            self.group_name = get_groupname_from_bandname(METIMAGE_BAND_NAMES_DICT[bandname])
            self._load(scale=1e6)

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename
        self.unit = 'micrometer'
        self.wavespace = 'wavelength'

    def _load(self, scale=1.0):
        """Load the METimage relative spectral responses."""
        LOG.debug(f'File: {str(self.requested_band_filename)}')
        threshold_response = 0.001

        ch_number = METIMAGE_BAND_NAMES.index(METIMAGE_BAND_NAMES_DICT_REVERSE[self.nc_band_name]) - \
            CHANNEL_GROUP_START_NUM.get(self.group_name)

        with ISRFReader(self.requested_band_filename) as r:
            shape = r.shape(self.group_name)
            num_detectors = shape[1]
            wvl = r.wavelength(self.group_name) * scale

            detectors = {}
            for detnum in range(num_detectors):
                resp = r.isrf(self.group_name, detector=detnum, channel=ch_number)
                max_resp = resp.max()
                resp = resp/max_resp
                detectors[f'det-{detnum+1}'] = {'wavelength': wvl[resp > threshold_response],
                                                'response': resp[resp > threshold_response]}

            self.rsr = detectors


def generate_metimage_file(platform_name):
    """Retrieve original RSR data and convert to internal hdf5 format."""
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
                if not (wvl.shape == det_wvl.shape) or not np.all(wvl == det_wvl):
                    LOG.warning("Wavelngth arrays are not the same among detectors")
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


if __name__ == "__main__":
    for platform_name in ["Metop-SG-A1", ]:
        generate_metimage_file(platform_name)
