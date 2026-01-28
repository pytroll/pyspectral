"""Read the FY-3G MERSI-RM relative spectral responses.

Data from https://img.nsmc.org.cn/PORTAL/NSMC/DATASERVICE/SRF/FY3G/FY-3G_MERSI-RM_SRF.zip
"""
import os

import numpy as np

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5
from pyspectral.utils import get_logger, logging_on

FY3_MERSIRM_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8']


class MersiRMRSR(InstrumentRSR):
    """Container for the FY-3 MERSI-RM RSR data."""

    def __init__(self, bandname, platform_name):
        """Initialise the FY-3 MERSI-RM relative spectral response data."""
        super(MersiRMRSR, self).__init__(bandname, platform_name, FY3_MERSIRM_BAND_NAMES)

        self.instrument = INSTRUMENTS.get(platform_name, 'mersi-rm')

        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()

        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        self.filename = self.requested_band_filename

    def _load(self, scale=0.001):
        """Load the MERSI-RM RSR data for the band requested.

        Wavelength is given in nanometers.
        """
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavelength',
                                    'response'],
                             skip_header=1)

        wavelength = data[0] * scale
        response = data[1]

        self.rsr = {'wavelength': wavelength, 'response': response}


def convert_mersirm():
    """Read original MERSI-RM RSR data and convert to common Pyspectral hdf5 format."""
    # For FY-3G
    tohdf5(MersiRMRSR, 'FY-3G', FY3_MERSIRM_BAND_NAMES)


if __name__ == "__main__":
    LOG = get_logger(__name__)
    logging_on()

    convert_mersirm()
