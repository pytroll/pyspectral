"""Read the VIRR relative spectral responses.

Data from http://gsics.nsmc.org.cn/portal/en/fycv/srf.html

"""

import logging
import os

import numpy as np

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import INSTRUMENTS
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

VIRR_BAND_NAMES = {
    'FY-3B': ['ch{:d}'.format(x) for x in range(1, 11)],
    'FY-3C': ['ch1', 'ch2'] + ['ch{:d}'.format(x) for x in range(6, 11)],
}


class VirrRSR(InstrumentRSR):
    """Container for the FY-3B/FY-3C VIRR RSR data."""

    def __init__(self, bandname, platform_name):
        """Verify that file exists and can be read."""
        super(VirrRSR, self).__init__(bandname, platform_name, VIRR_BAND_NAMES[platform_name])

        self.instrument = INSTRUMENTS.get(platform_name, 'virr')
        self._get_options_from_config()
        self._get_bandfilenames()

        LOG.debug("Filenames: %s", str(self.filenames))
        if self.filenames[bandname] and os.path.exists(self.filenames[bandname]):
            self.requested_band_filename = self.filenames[bandname]
            self._load()
        else:
            LOG.warning("Couldn't find an existing file for this band: %s",
                        str(self.bandname))

        # To be compatible with VIIRS....
        self.filename = self.requested_band_filename

    def _load(self, scale=0.001):
        """Load the VIRR RSR data for the band requested.

        Wavelength is given in nanometers.
        """
        data = np.genfromtxt(self.requested_band_filename,
                             unpack=True,
                             names=['wavelength',
                                    'response'],
                             skip_header=0)

        wavelength = data['wavelength'] * scale
        response = data['response']

        self.rsr = {'wavelength': wavelength, 'response': response}


if __name__ == "__main__":
    for platform_name, band_names in VIRR_BAND_NAMES.items():
        tohdf5(VirrRSR, platform_name, band_names)
