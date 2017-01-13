#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2015, 2016, 2017 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>
#   Panu Lahtinen <panu.lahtinen@fmi.fi>

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

"""Main module"""

from pyspectral.version import __version__
import logging
import os

LOG = logging.getLogger(__name__)

import pkg_resources
BUILTIN_CONFIG_FILE = pkg_resources.resource_filename(__name__,
                                                      os.path.join('etc', 'pyspectral.cfg'))

CONFIG_FILE = os.environ.get('PSP_CONFIG_FILE')

if CONFIG_FILE is not None and (not os.path.exists(CONFIG_FILE) or
                                not os.path.isfile(CONFIG_FILE)):
    raise IOError(str(CONFIG_FILE) + " pointed to by the environment " +
                  "variable PSP_CONFIG_FILE is not a file or does not exist!")


def get_config():
    """Get config from file"""

    import ConfigParser

    conf = ConfigParser.ConfigParser()
    conf.read(BUILTIN_CONFIG_FILE)
    if CONFIG_FILE is not None:
        try:
            conf.read(CONFIG_FILE)
        except ConfigParser.NoSectionError:
            LOG.info('Failed reading configuration file: %s',
                     str(CONFIG_FILE))

    return conf
