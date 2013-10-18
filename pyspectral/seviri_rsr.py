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

"""Interface to the SEVIRI spectral response functions for all four MSG
satellites
"""

import logging
LOG = logging.getLogger(__name__)

import ConfigParser
import os

try:
    CONFIG_FILE = os.environ['PSP_CONFIG_FILE']
except KeyError:
    LOG.exception('Environment variable PSP_CONFIG_FILE not set!')
    raise

if not os.path.exists(CONFIG_FILE) or not os.path.isfile(CONFIG_FILE):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " + 
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")


from xlrd import open_workbook
import numpy as np

def load(filename=None):
    """Read the SEVIRI rsr data"""

    conf = ConfigParser.ConfigParser()
    try:
        conf.read(CONFIG_FILE)
    except ConfigParser.NoSectionError:
        LOG.exception('Failed reading configuration file: ' + str(CONFIG_FILE))
        raise

    options = {}
    for option, value in conf.items('seviri', raw = True):
        options[option] = value

    seviri_path = options.get('path')
    if not filename:
        filename = seviri_path


    wb = open_workbook(filename)

    channel_rsr = {}
    sheet_names = []
    for sheet in wb.sheets():
        if sheet.name in ['Info', 'Requirements']:
            continue
        ch_name = sheet.name.strip()
        sheet_names.append(sheet.name.strip())

        channel_rsr[ch_name] = {'wavelength': None, 
                                'met8': None, 
                                'met9': None, 
                                'met10': None, 
                                'met11': None}

        if ch_name.startswith('IR'):
            wvl = np.array(sheet.col_values(0, start_rowx=13, end_rowx=113))
            met8_95 = np.array(sheet.col_values(1, start_rowx=13, end_rowx=113))
            met9_95 = np.array(sheet.col_values(3, start_rowx=13, end_rowx=113))
            met10_95 = np.array(sheet.col_values(5, start_rowx=13, end_rowx=113))
            met11_95 = np.array(sheet.col_values(7, start_rowx=13, end_rowx=113))
            met8_85 = np.array(sheet.col_values(2, start_rowx=13, end_rowx=113))
            met9_85 = np.array(sheet.col_values(4, start_rowx=13, end_rowx=113))
            met10_85 = np.array(sheet.col_values(6, start_rowx=13, end_rowx=113))
            met11_85 = np.array(sheet.col_values(8, start_rowx=13, end_rowx=113))
            channel_rsr[ch_name]['met8'] = {'95': met8_95, '85': met8_85}
            channel_rsr[ch_name]['met9'] = {'95': met9_95, '85': met9_85}
            channel_rsr[ch_name]['met10'] = {'95': met10_95, '85': met10_85}
            channel_rsr[ch_name]['met11'] = {'95': met11_95, '85': met11_85}
        else:
            wvl = np.array(sheet.col_values(0, start_rowx=12, end_rowx=112))
            met8 = np.array(sheet.col_values(1, start_rowx=12, end_rowx=112))
            met9 = np.array(sheet.col_values(2, start_rowx=12, end_rowx=112))
            met10 = np.array(sheet.col_values(3, start_rowx=12, end_rowx=112))
            met11 = np.array(sheet.col_values(4, start_rowx=12, end_rowx=112))
            channel_rsr[ch_name]['met8'] = met8
            channel_rsr[ch_name]['met9'] = met9
            channel_rsr[ch_name]['met10'] = met10
            channel_rsr[ch_name]['met11'] = met11

        channel_rsr[ch_name]['wavelength'] = wvl

    return channel_rsr
