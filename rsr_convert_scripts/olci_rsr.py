#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 - 2022 Pytroll developers
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

"""Reading the Sentinel-3 OLCI relative spectral responses.

https://sentinel.esa.int/documents/247904/322304/OLCI+SRF+%28NetCDF%29/

https://sentinel.esa.int/web/sentinel/technical-guides/
sentinel-3-olci/olci-instrument/spectral-response-function-data

"""

import logging
import os.path

from netCDF4 import Dataset

from pyspectral.raw_reader import InstrumentRSR
from pyspectral.utils import convert2hdf5 as tohdf5

LOG = logging.getLogger(__name__)

RSRFILE = {'Sentinel-3A': '/home/a000680/data/SpectralResponses/olci/S3A_OL_SRF_20160713_mean_rsr.nc4',
           'Sentinel-3B': '/home/a000680/data/SpectralResponses/olciB/S3B_OL_SRF_0_20180109_mean_rsr.nc4'}


OLCI_BAND_NAMES = ['Oa01', 'Oa02', 'Oa03', 'Oa04',
                   'Oa05', 'Oa06', 'Oa07', 'Oa08',
                   'Oa09', 'Oa10', 'Oa11', 'Oa12',
                   'Oa13', 'Oa14', 'Oa15', 'Oa16',
                   'Oa17', 'Oa18', 'Oa19', 'Oa20',
                   'Oa21']


class OlciRSR(InstrumentRSR):
    """Class for Sentinel OLCI RSR."""

    def __init__(self, bandname, platform_name):
        """Read the OLCI relative spectral responses for all channels."""
        super(OlciRSR, self).__init__(bandname, platform_name)

        self.instrument = 'olci'
        self._get_options_from_config()

        LOG.debug("Filename: %s", str(self.path))
        if os.path.exists(self.path):
            self._load()
        else:
            raise IOError("Couldn't find an existing file for this band: " +
                          str(self.bandname))

    def _load(self, scale=0.001):
        """Load the OLCI relative spectral responses."""
        ncf = Dataset(self.path, 'r')

        bandnum = OLCI_BAND_NAMES.index(self.bandname)
        # cam = 0
        # view = 0
        # resp = ncf.variables[
        #     'spectral_response_function'][bandnum, cam, view, :]
        # wvl = ncf.variables[
        #     'spectral_response_function_wavelength'][bandnum, cam, view, :] * scale
        resp = ncf.variables[
            'mean_spectral_response_function'][bandnum, :]
        wvl = ncf.variables[
            'mean_spectral_response_function_wavelength'][bandnum, :] * scale

        self.rsr = {'wavelength': wvl, 'response': resp}


def testplot():
    """Just making a plot of the OLCI spectral response functions.

    There are 21 bands.
    For each band there are 5 cameras and 3 views (west, centre and east).
    Doing band 1 here, only.
    """
    import pylab
    from matplotlib import rcParams

    this = Dataset(RSRFILE, 'r')

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
            label = 'Camera {0:d} - view {1:d}'.format(cam + 1, view + 1)
            ax.plot(wvl, resp, label=label)
    ax.set_xlim(380, 430)
    ax.legend()
    fig.savefig('olci_band1.png')


if __name__ == "__main__":
    for platform_name in ['Sentinel-3B', ]:
        tohdf5(OlciRSR, platform_name, OLCI_BAND_NAMES)
