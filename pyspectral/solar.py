#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2023 Pytroll developers
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

"""
Read solar irradiances and calculate solar flux.

Module to read solar irradiance spectra and calculate the solar flux over
various instrument bands given their relative spectral response functions
"""

import logging
from pathlib import Path

import numpy as np
from scipy.integrate import trapezoid

LOG = logging.getLogger(__name__)

# STANDARD SPECTRA from Air Mass Zero: http://rredc.nrel.gov/solar/spectra/am0/
#    * 2000 ASTM Standard Extraterrestrial Spectrum Reference E-490-00
#      (119.5 - 1,000,000.0 nm)
TOTAL_IRRADIANCE_SPECTRUM_2000ASTM = Path(__file__).resolve().parent / "data" / "e490_00a.dat"


class SolarIrradianceSpectrum(object):
    """
    Total Top of Atmosphere (TOA) Solar Irradiance Spectrum.

    Wavelength is in units of microns (10^-6 m).
    The spectral Irradiance in the file TOTAL_IRRADIANCE_SPECTRUM_2000ASTM is
    in units of W/m^2/micron
    """

    def __init__(self, filename=TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, **options):
        """Initialize the top of atmosphere solar irradiance spectrum object from file.

        By default, this will use the following spectra:
        2000 ASTM Standard Extraterrestrial Spectrum Reference E-490-00

        To use a different spectra, specify the `filename` when initialising the class.

        Input:
        filename: Filename of the solar irradiance spectrum (default: 2000 ASTM)
        options:
          dlambda:
            Delta wavelength: the step in wavelength defining the resolution on
            which to integrate/convolute.
            Default is 0.005 if 'wavespace' is 'wavelength' and 2.0 if 'wavenumber'.
          wavespace:
            It is possible to specify if the solar irradiance spectrum should
            be given in terms of wavelength (default) or in terms of
            wavenumber. If the latter is desired 'wavespace' should be set to
            'wavenumber'.

        """
        self.wavelength = None
        self.wavenumber = None
        self.irradiance = None
        self.filename = filename
        self.ipol_wavelength = None
        self.ipol_irradiance = None
        self.ipol_channel_response = None
        # Delta wavelength used when resampling the
        # spectrum to an evenly spaced grid (using interpolation)
        if 'wavespace' in options:
            self.wavespace = options['wavespace']
        else:
            self.wavespace = 'wavelength'
        if 'dlambda' in options:
            self._dlambda = options['dlambda']
        else:
            if self.wavespace == 'wavelength':
                self._dlambda = 0.005
            else:
                self._dlambda = 1. / (0.005 * 100.)

        self._load()

        if self.wavespace == 'wavenumber':
            self.convert2wavenumber()
            self.units = {'irradiance': 'mW/m^2 (cm^{-1})^{-1}',
                          'flux': 'mW/m^2'}
        else:
            self.units = {'irradiance': '$W/m^2 (1e-6*m)^{-1})',
                          'flux': 'W/m^2'}

    def convert2wavenumber(self):
        """Convert from wavelengths to wavenumber.

        Units:
          Wavelength: micro meters (1e-6 m)
          Wavenumber: cm-1

        """
        self.wavenumber = 1. / (1e-4 * self.wavelength[::-1])
        self.irradiance = (self.irradiance[::-1] *
                           self.wavelength[::-1] * self.wavelength[::-1] * 0.1)
        self.wavelength = None

    def _load(self):
        """Read the tabulated spectral irradiance data from file."""
        self.wavelength, self.irradiance = \
            np.genfromtxt(self.filename, unpack=True)

    def solar_constant(self):
        """Calculate the solar constant."""
        if self.wavenumber is not None:
            return trapezoid(self.irradiance, self.wavenumber)
        if self.wavelength is not None:
            return trapezoid(self.irradiance, self.wavelength)

        raise TypeError('Neither wavelengths nor wavenumbers available!')

    def inband_solarflux(self, rsr, scale=1.0, **options):
        """Get the in band solar flux.

        Derive the in-band integrated solar flux for a given instrument relative
        spectral response valid for an earth-sun distance of one AU.

        This is the total solar flux in the band in units of W/m^2.
        """
        return self._band_calculations(rsr, True, scale, **options)

    def inband_solarirradiance(self, rsr, scale=1.0, **options):
        """Get the in band solar irradiance.

        Derive the in-band spectral solar irradiance for a given instrument relative
        spectral response valid for an earth-sun distance of one AU.

        This is the total solar flux in the band convolved with the
        spectral response function in units of W/m^2/micron.
        """
        return self._band_calculations(rsr, False, scale, **options)

    def _band_calculations(self, rsr, flux, scale, **options):
        """Derive in band solar flux.

        Derive the in band solar flux or in band solar irradiance for a given
        instrument relative spectral response valid for an earth-sun distance
        of one AU.

        rsr: Relative Spectral Response (one detector only)
        Dictionary with two members 'wavelength' and 'response'
        options:
        detector: Detector number (between 1 and N - N=number of detectors
        for channel)

        """
        from scipy.interpolate import InterpolatedUnivariateSpline

        if 'detector' in options:
            detector = options['detector']
        else:
            detector = 1

        # Resample/Interpolate the response curve:
        if self.wavespace == 'wavelength':
            if 'response' in rsr:
                wvl = rsr['wavelength'] * scale
                resp = rsr['response']
            else:
                wvl = rsr['det-{0:d}'.format(detector)]['wavelength'] * scale
                resp = rsr['det-{0:d}'.format(detector)]['response']
        else:
            if 'response' in rsr:
                wvl = rsr['wavenumber'] * scale
                resp = rsr['response']
            else:
                wvl = rsr['det-{0:d}'.format(detector)]['wavenumber'] * scale
                resp = rsr['det-{0:d}'.format(detector)]['response']

        start = wvl[0]
        end = wvl[-1]
        # print "Start and end: ", start, end
        LOG.debug("Begin and end wavelength/wavenumber: %f %f ", start, end)
        dlambda = self._dlambda
        xspl = np.linspace(start, end, int(round((end - start) / self._dlambda)) + 1)

        ius = InterpolatedUnivariateSpline(wvl, resp)
        resp_ipol = ius(xspl)

        # Interpolate solar spectrum to specified resolution and over specified
        # Spectral interval:
        self.interpolate(dlambda=dlambda, ival_wavelength=(start, end))

        # Mask out outside the response curve:
        maskidx = np.logical_and(np.greater_equal(self.ipol_wavelength, start),
                                 np.less_equal(self.ipol_wavelength, end))
        wvl = np.repeat(self.ipol_wavelength, maskidx)
        irr = np.repeat(self.ipol_irradiance, maskidx)

        # Calculate the solar-flux: (w/m2)
        if flux:
            return trapezoid(irr * resp_ipol, wvl)

        # Divide by the equivalent band width:
        return trapezoid(irr * resp_ipol, wvl) / trapezoid(resp_ipol, wvl)

    def interpolate(self, **options):
        """Interpolate Irradiance to a specified evenly spaced resolution/grid.

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
        from scipy.interpolate import InterpolatedUnivariateSpline

        if 'ival_wavelength' in options:
            ival_wavelength = options['ival_wavelength']
        else:
            ival_wavelength = None

        if 'dlambda' in options:
            self._dlambda = options['dlambda']

        if ival_wavelength is None:
            if self.wavespace == 'wavelength':
                start = self.wavelength[0]
                end = self.wavelength[-1]
            else:
                start = self.wavenumber[0]
                end = self.wavenumber[-1]
        else:
            start, end = ival_wavelength

        xspl = np.linspace(start, end, int(round((end - start) / self._dlambda)) + 1)
        if self.wavespace == 'wavelength':
            ius = InterpolatedUnivariateSpline(
                self.wavelength, self.irradiance)
        else:
            ius = InterpolatedUnivariateSpline(
                self.wavenumber, self.irradiance)
        yspl = ius(xspl)

        self.ipol_wavelength = xspl
        self.ipol_irradiance = yspl

    def plot(self, plotname=None, **options):
        """Plot the data."""
        if 'color' in options:
            color = options['color']
        else:
            color = 'blue'

        if self.wavespace == "wavelength":
            xlabel = r"Wavelength ($\mu m$)"
            ylabel = r"Irradiance ($W/(m^2 \mu m$))"
            xlim = [0, 4.2]
            xwl, yir = self.wavelength, self.irradiance
        elif self.wavespace == "wavenumber":
            xlabel = "Wavenumber ($cm^{-1}$)"
            ylabel = "Irradiance ($mW/m^2 (cm^{-1})^{-1}$))"
            xlim = [0, 35000]
            xwl, yir = self.wavenumber, self.irradiance
        else:
            raise TypeError('Neither wavelengths nor wavenumbers available!')

        from matplotlib import pyplot as plt
        from matplotlib import rcParams
        rcParams['text.usetex'] = True
        rcParams['text.latex.unicode'] = True

        fig, axl = plt.subplots(figsize=(8, 4))
        plot_title = "Solar Irradiance Spectrum"
        axl.set_title(plot_title)

        axl.plot(xwl, yir, '-', color=color)

        axl.set_xlabel(xlabel)
        axl.set_ylabel(ylabel)
        axl.set_xlim(xlim)
        axl.set_ylim([0, yir.max()])
        axl.grid(True)

        if plotname is None:
            plt.show()
        else:
            fig.savefig(plotname)
