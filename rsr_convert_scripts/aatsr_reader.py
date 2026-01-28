"""Interface to the original Envisat AATSR spectral response functions.

From ESA: http://envisat.esa.int/handbooks/aatsr/aux-files/consolidatedsrfs.xls

"""
import logging

import numpy as np
from xlrd import open_workbook

from pyspectral.config import get_config
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

AATSR_BAND_NAMES = ['ir12', 'ir11', 'ir37', 'v16', 'v870', 'v659', 'v555']


class AatsrRSR(object):
    """Class for Envisat AATSR RSR."""

    def __init__(self, bandname, platform_name='Envisat'):
        """Read the aatsr relative spectral responses for all channels."""
        self.platform_name = platform_name
        self.instrument = 'aatsr'
        self.bandname = bandname
        self.rsr = None

        options = get_config()

        self.aatsr_path = options[
            self.platform_name + '-' + self.instrument].get('path')

        self.output_dir = options.get('rsr_dir', './')

        self._load()

    def _load(self, filename=None):
        """Read the AATSR rsr data."""
        if not filename:
            filename = self.aatsr_path

        wb_ = open_workbook(filename)

        for sheet in wb_.sheets():
            ch_name = sheet.name.strip()
            if ch_name == 'aatsr_' + self.bandname:

                data = np.array([s.split() for s in
                                 sheet.col_values(0,
                                                  start_rowx=3, end_rowx=258)])
                data = data.astype('f')
                wvl = data[:, 0]
                resp = data[:, 1]

                self.rsr = {'wavelength': wvl, 'response': resp}


if __name__ == "__main__":
    tohdf5(AatsrRSR, 'Envisat', AATSR_BAND_NAMES)
