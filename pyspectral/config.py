#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, 2018 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

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

"""PySpectral configuration directory and file handling
"""

import logging
import os
from os.path import expanduser
from appdirs import AppDirs
import yaml
from collections import Mapping
import pkg_resources


LOG = logging.getLogger(__name__)

BUILTIN_CONFIG_FILE = pkg_resources.resource_filename(__name__,
                                                      os.path.join('etc', 'pyspectral.yaml'))


CONFIG_FILE = os.environ.get('PSP_CONFIG_FILE')

if CONFIG_FILE is not None and (not os.path.exists(CONFIG_FILE) or
                                not os.path.isfile(CONFIG_FILE)):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")


def recursive_dict_update(d, u):
    """Recursive dictionary update using

    Copied from:

        http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

    """
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def get_config():
    """Get the configuration from file"""
    if CONFIG_FILE is not None:
        configfile = CONFIG_FILE
    else:
        configfile = BUILTIN_CONFIG_FILE

    config = {}
    with open(configfile, 'r') as fp_:
        config = recursive_dict_update(config, yaml.load(fp_))

    app_dirs = AppDirs('pyspectral', 'pytroll')
    user_datadir = app_dirs.user_data_dir
    config['rsr_dir'] = expanduser(config.get('rsr_dir', user_datadir))
    config['rayleigh_dir'] = expanduser(config.get('rayleigh_dir', user_datadir))

    return config
