"""Read the MTG FCI relative spectral response functions.

Data from EUMETSAT:
https://sftp.eumetsat.int/public/folder/UsCVknVOOkSyCdgpMimJNQ/User-Materials/MTGUP/Materials/FCI-SRF_Apr2022/
"""

import logging

from netCDF4 import Dataset

from pyspectral.bandnames import BANDNAMES
from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

FCI_BAND_NAMES = list(BANDNAMES['fci'].values())


class FciRSR(InstrumentRSR):
    """Container for the MTG FCI RSR data."""

    def __init__(self, bandname, platform_name):
        """MTG FCI RSR data container."""
        super().__init__(bandname, platform_name)

        self.instrument = 'fci'
        self._get_options_from_config()

        LOG.debug("Filename with all bands: %s", str(self.filename))
        self._load()

    def _load(self, scale=1000000.0):
        """Load the FCI RSR data for the band requested."""
        LOG.debug("File: %s", str(self.filename))

        ncf = Dataset(self.path / self.filename, 'r')

        wvl = ncf.variables['wavelength'][:] * scale
        resp = ncf.variables['srf'][:]

        bandnames = ncf.variables['channel_id'][:]
        for idx, band_name in enumerate(bandnames):
            if band_name == self.bandname:
                self.rsr = {'wavelength': wvl[:, idx], 'response': resp[:, idx]}


def main():
    """Create the internal Pyspectral hdf5 output for FCI."""
    for platform_name in ["Meteosat-12", 'MTG-I1']:
        tohdf5(FciRSR, platform_name, FCI_BAND_NAMES)


if __name__ == "__main__":
    main()
