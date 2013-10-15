#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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
Module to read solar irradiance spectra and calculate the solar flux over
various instrument bands given their relative spectral response functions
"""

import logging
LOG = logging.getLogger(__name__)

from pkg_resources import resource_filename

# STANDARD SPECTRA from Air Mass Zero: http://rredc.nrel.gov/solar/spectra/am0/
#    * 2000 ASTM Standard Extraterrestrial Spectrum Reference E-490-00   
#      (119.5 - 1,000,000.0 nm)
TOTAL_IRRADIANCE_SPECTRUM_2000ASTM = resource_filename(__name__, 
                                                       'data/e490_00a.dat')



class SolarIrradianceSpectrum(object):
    """Total Top of Atmosphere (TOA) Solar Irradiance Spectrum
    Wavelength is in units of microns (10^-6 m)
    The spectral Irradiance is in units of W/m^2/micron
    """
    def __init__(self, filename, **options):
        """
        Input:
          filename: Filename of the solar irradiance spectrum
          dlambda:
          Delta wavelength => the step in wavelength defining the resolution on which to 
          integrate/convolute.
        """
        self.wavelength = None
        self.irradiance = None
        self.filename = filename
        self.ipol_wavelength = None
        self.ipol_irradiance = None
        self.ipol_channel_response = None
        # Delta wavelength used when resampling the 
        # spectrum to an evenly spaced grid (using interpolation)
        if 'dlambda' in options:
            self._dlambda = options['dlambda']
        else:
            self._dlambda = 0.005
        
    def read(self):
        """Read the tabulated spectral irradiance data from file"""
        import numpy as np
        self.wavelength, self.irradiance = np.genfromtxt(self.filename, unpack=True)


    def solar_flux_over_band(self, rsr, **options):
        """Derive the Solar Flux for a given instrument relative spectral response
        rsr: Relative Spectral Response (one detector only)
             Dictionary with two members 'wavelength' and 'response'
        options:
        """
        import numpy as np
        from scipy.interpolate import InterpolatedUnivariateSpline

        if 'detector' in options:
            detector = options['detector']
        else:
            detector = 1

        # Resample/Interpolate the response curve:
        if 'wavelength' in rsr:
            wvl = rsr['wavelength']
            resp = rsr['response']
        else:
            wvl = rsr['det-%d' % detector]['wavelength']
            resp = rsr['det-%d' % detector]['response']

        start = wvl[0]
        end = wvl[-1]
        LOG.debug("start and end wavelength interval: %f %f " % (start, end))
        dlambda = self._dlambda
        xspl = np.linspace(start, end, (end-start)/dlambda)

        ius = InterpolatedUnivariateSpline(wvl, resp)
        resp_ipol = ius(xspl)

        # Interpolate solar spectrum to specified resolution and over specified
        # Spectral interval:
        self.interpolate(dlambda = dlambda, ival_wavelength = (start, end))

        # Mask out outside the response curve:
        maskidx = np.logical_and(np.greater_equal(self.ipol_wavelength, start),
                                 np.less_equal(self.ipol_wavelength, end))
        wvl = np.repeat(self.ipol_wavelength, maskidx)
        irr = np.repeat(self.ipol_irradiance, maskidx)

        # Calculate the solar-flux: w/m2
        flux = np.sum(irr*resp_ipol*dlambda)
        return flux


    def interpolate(self, **options):
        """Interpolate Irradiance to a specified evenly spaced resolution/grid
        This is necessary to make integration and folding (with a channel
        relative spectral response) straightforward.
 
        dlambda = wavelength interval in microns
        start = Start of the wavelength interval (left/lower)
        end = End of the wavelength interval (right/upper end)
        options:
          dlambda: Delta wavelength used when interpolating/resampling
          ival_wavelength: Tuple. The start and end interval in wavelength
          space, defining where to integrate/convolute the spectral response
          curve on the spectral irradiance data.
        """        
        from numpy import linspace
        from scipy.interpolate import InterpolatedUnivariateSpline
        
        # The user defined wavelength span is not yet used:
        # FIXME!
        if 'ival_wavelength' in options:
            ival_wavelength = options['ival_wavelength']
        else:
            ival_wavelength = None
        
        if 'dlambda' in options:
            self._dlambda = options['dlambda']

        if ival_wavelength == None:
            start = self.wavelength[0]
            end = self.wavelength[-1]
        else:
            start, end = ival_wavelength

        xspl = linspace(start, end, (end-start)/self._dlambda)
        ius = InterpolatedUnivariateSpline(self.wavelength, self.irradiance)
        yspl = ius(xspl)

        self.ipol_wavelength = xspl
        self.ipol_irradiance = yspl


def plot(xwl, yir, plotname = None, color='blue'):
    """Plot the data"""
    import pylab 
    from matplotlib import rcParams
    rcParams['text.usetex'] = True
    rcParams['text.latex.unicode'] = True

    fig = pylab.figure(figsize=(12,6))
    plot_title = "Solar Irradiance Spectrum"
    pylab.title(plot_title)
    ax = fig.add_subplot(111)
    
    ax.plot(xwl, yir, '-', color=color)

    pylab.xlabel("Wavelength ($\mu m$)")
    pylab.ylabel("Irradiance ($W/(m^2*sr* \mu m$))")
    pylab.xlim([0, 4.2])
    pylab.ylim([0, max(yir)])
    ax.grid(True)

    if plotname == None:
        pylab.show()
    else:
        fig.savefig(plotname)
