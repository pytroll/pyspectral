#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2022 Pytroll developers
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

"""PySpectral configuration directory and file handling."""

import logging
import os
from collections.abc import Mapping
from os.path import expanduser
from pathlib import Path

import yaml
from platformdirs import AppDirs

try:
    from yaml import UnsafeLoader
except ImportError:
    from yaml import Loader as UnsafeLoader


LOG = logging.getLogger(__name__)

BUILTIN_CONFIG_FILE = Path(__file__).resolve().parent / "etc" / "pyspectral.yaml"


def recursive_dict_update(d, u):
    """Recursive dictionary update.

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


def get_config(config_file: str | Path = None) -> dict:
    """Get configuration options from YAML file."""
    if config_file is None:
        config_file = _get_env_or_builtin_config_path()

    config = {}
    with open(config_file, 'r') as fp_:
        config = recursive_dict_update(config, yaml.load(fp_, Loader=UnsafeLoader))

    app_dirs = AppDirs('pyspectral', 'pytroll')
    user_datadir = app_dirs.user_data_dir
    config['rsr_dir'] = expanduser(config.get('rsr_dir', user_datadir))
    config['rayleigh_dir'] = expanduser(config.get('rayleigh_dir', user_datadir))
    os.makedirs(config['rsr_dir'], exist_ok=True)
    os.makedirs(config['rayleigh_dir'], exist_ok=True)

    return config


def _get_env_or_builtin_config_path() -> Path:
    config_file = os.environ.get('PSP_CONFIG_FILE')
    if config_file is not None and not os.path.isfile(config_file):
        raise IOError(f"{config_file} pointed to by the environment variable "
                      f"'PSP_CONFIG_FILE' is not a file or does not exist!")
    if config_file is None:
        return BUILTIN_CONFIG_FILE
    return Path(config_file)
