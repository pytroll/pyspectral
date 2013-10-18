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

"""Reader for various Relative Spectral Response curves from various satellite
sensors
"""

import numpy as np
from pkg_resources import resource_filename

MODIS_AQUA_RESPONSES = {}
for bnum in [5, 6, 7] + range(20, 37):
    fname = "%.2d.tv.1pct.det" % (bnum)
    MODIS_AQUA_RESPONSES['%d' % bnum] = resource_filename(__name__, 
                                                          'data/modis/aqua/%s' % fname)
for bnum in range(1,20):
    if bnum not in [5, 6, 7]:
        fname = "%.2d.amb.1pct.det" % (bnum)
    MODIS_AQUA_RESPONSES['%d' % bnum] = resource_filename(__name__, 
                                                          'data/modis/aqua/%s' % fname)

MODIS_TERRA_RESPONSES = {}
for bnum in range(1,37):
    fname = "rsr.%d.oobd.det" % (bnum)
    MODIS_TERRA_RESPONSES['%d' % bnum] = resource_filename(__name__, 
                                                          'data/modis/terra/Reference_RSR_Dataset/%s' % fname)


# ----------------------------------------------------
class RelativeSpectralResponse(object):
    """Container for the relative spectral response functions for various
    satellite imagers
    """
    def __init__(self, platform='noaa', satnum=19, instrument='avhrr', 
                 sort = True):
        self.platform = platform
        self.satnum = satnum
        self.instrument = instrument        
        self.filenames = {}
        self.filename = None
        self.rsr = {}
        self._sort = sort
        
        # So far only support for Modis:
        if self.platform == "eos":
            self.satellite_id = "%s-%d" % (self.platform, self.satnum)
            if self.satnum == 1:
                for bnum in range(1, 37):
                    self.filenames = MODIS_TERRA_RESPONSES
                self.filenames['3.7'] = self.filenames['20']
            elif self.satnum == 2:
                for bnum in range(1, 37):
                    self.filenames = MODIS_AQUA_RESPONSES
                self.filenames['3.7'] = self.filenames['20']
            else:
                raise IOError("Invalid satellite id: %s-%d" % (self.platform, self.satnum))

    def read(self, **args):
        """Read the relative spectral response data from file. Be aware that
        these raw data may not be sorted. They may not have monotonically
        increasing wavelengths and there may be duplicates. The sort method
        must be called to fix that. This is done on default.
        """

        if 'channel' in args:
            channel = args['channel']
        else:
            channel = None # '3.7'        
        if 'band' in args:
            band = args['band']
        else:
            band = None # 'M12'
        if 'scale' in args:
            scale = args['scale']
        else:
            scale = 1.0

        if self.filename:
            filename = self.filename
        elif channel in self.filenames:
            filename = self.filenames[channel]
        elif band in self.filenames:
            filename = self.filenames[band]
        else:
            raise IOError('No band or channel specified!')


        if self.instrument == "modis" and self.platform == "eos":
            #if self.satnum == 1:
            #    scale = 1.0 # Scale should be 0.001 for VIS/NIR channels
            #elif self.satnum == 2:
            #    scale = 0.001
            #else:
            #    IOError("Satellite number %d for platform %s not supported!" % \
            #                (self.satnum, self.platform))
            detector = read_modis_response(filename, scale)


        else:
            raise IOError("Platform %s or imager " % self.platform + 
                          "%s not supported yet!" % self.instrument)

        self.rsr = detector
        if self._sort:
            self.sort()

    def sort(self):
        """Sort the data so that x is monotonically increasing and contains
        no duplicates."""
        if 'wavelength' in self.rsr:
            # Only one detector apparently:
            self.rsr['wavelength'], self.rsr['response'] = \
                sort_data(self.rsr['wavelength'], self.rsr['response'])
        else:
            for detector_name in self.rsr:
                # print "Sorting data (%s,%s): Detector name = %s" % (self.platform,
                #                                                     self.instrument,
                #                                                     detector_name)
                self.rsr[detector_name]['wavelength'], self.rsr[detector_name]['response'] = \
                    sort_data(self.rsr[detector_name]['wavelength'], self.rsr[detector_name]['response'])


# ---------------------------------------------------------------------------
def sort_data(x, y):
    """Sort the data so that x is monotonically increasing and contains
    no duplicates.
    """
    # Sort data
    j = np.argsort(x)
    x = x[j]
    y = y[j]

    # De-duplicate data
    mask = np.r_[True, (np.diff(x) > 0)]
    if not mask.all():
        numof_duplicates = np.repeat(mask, np.equal(mask, False)).shape[0]

    x = x[mask]
    y = y[mask]

    return x, y

# -------------------------------------------------------------
def read_modis_response(filename, scale=1.0):
    """Read the Terra/Aqua MODIS relative spectral responses. Be aware that
    MODIS has several detectors (more than one) compared to e.g. AVHRR which
    has always only one.
    """
    fd = open(filename, "r")
    lines = fd.readlines()
    fd.close()

    # The IR channels seem to be in microns, whereas the short wave channels are
    # in nanometers! For VIS/NIR scale should be 0.001
    detectors = {}
    for line in lines:
        if line.find("#") == 0:
            continue
        dummy1, dummy2, s1, s2 = line.split()
        detector_name = 'det-%d' % int(dummy2)
        if detector_name not in detectors:
            detectors[detector_name] = {'wavelength': [], 'response': []}
            
        detectors[detector_name]['wavelength'].append(float(s1)*scale)
        detectors[detector_name]['response'].append(float(s2))

    for key in detectors:
        detectors[key]['wavelength'] = np.array(detectors[key]['wavelength'])
        detectors[key]['response'] = np.array(detectors[key]['response'])

    return detectors
