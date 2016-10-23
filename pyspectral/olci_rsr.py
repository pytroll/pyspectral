#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbro@smhi.se>

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

"""
Reading the Sentinel-3 OLCI relative spectral responses

https://sentinel.esa.int/documents/247904/322304/OLCI+SRF+%28NetCDF%29/15cfd7a6-b7bc-4051-87f8-c35d765ae43a
"""

RSRFILE = '/home/a000680/data/SpectralResponses/olci/OLCISRFNetCDF.nc4'

from netCDF4 import Dataset
import os.path
from pyspectral.utils import convert2hdf5 as tohdf5

import logging
LOG = logging.getLogger(__name__)


OLCI_BAND_NAMES = ['ch1', 'ch2', 'ch3', 'ch4',
                   'ch5', 'ch6', 'ch7', 'ch8',
                   'ch9', 'ch10', 'ch11', 'ch12',
                   'ch13', 'ch14', 'ch15', 'ch16',
                   'ch17', 'ch18', 'ch19', 'ch20']

from pyspectral.raw_reader import InstrumentRSR


class OlciRSR(InstrumentRSR):

    """Class for Envisat SLSTR RSR"""

    def __init__(self, bandname, platform_name):
        """
        Read the OLCI relative spectral responses for all channels.

        """
        super(OlciRSR, self).__init__(bandname, platform_name)

        self.instrument = 'olci'
        self._get_options_from_config()

        LOG.debug("Filename: %s", str(self.path))
        if os.path.exists(self.path):
            self._load(bandname)
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, bandname, scale=0.001):
        """Load the SLSTR relative spectral responses
        """

        ncf = Dataset(self.path, 'r')

        bandnum = OLCI_BAND_NAMES.index(bandname)
        cam = 0
        view = 0
        resp = ncf.variables[
            'spectral_response_function'][bandnum, cam, view, :]
        wvl = ncf.variables[
            'spectral_response_function_wavelength'][bandnum, cam, view, :] * scale
        self.rsr = {'wavelength': wvl, 'response': resp}


def main():
    """Main"""
    for platform_name in ['Sentinel-3A', ]:
        tohdf5(OlciRSR, platform_name, OLCI_BAND_NAMES)


def testplot():

    this = Dataset(RSRFILE, 'r')
    # There are 21 bands
    # For each band there are 5 cameras and 3 views (west, centre and east)
    # Band 1:

    import pylab
    from matplotlib import rcParams
    rcParams['text.usetex'] = True
    rcParams['text.latex.unicode'] = True

    fig = pylab.figure(figsize=(11, 6))
    plot_title = "S-3 OLCI: Relative Spectral Responses"
    pylab.title(plot_title)
    ax = fig.add_subplot(111)

    for cam in range(5):
        for view in range(3):
            resp = this.variables[
                'spectral_response_function'][0, cam, view, :]
            wvl = this.variables[
                'spectral_response_function_wavelength'][0, cam, view, :]
            label = 'Camera %d - view %d' % (cam + 1, view + 1)
            ax.plot(wvl, resp, label=label)
    ax.set_xlim(380, 430)
    ax.legend()
    fig.savefig('olci_band1.png')
    # pylab.show()

if __name__ == "__main__":

    main()
