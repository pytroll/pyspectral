"""PySpectral configuration directory and file handling."""

import logging
import os
from collections.abc import Mapping
from os.path import expanduser
from pathlib import Path
from typing import Any

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


def get_config(config_file: str | Path | None = None) -> dict:
    """Get configuration options from YAML file."""
    if config_file is None:
        config_file = _get_env_or_builtin_config_path()

    config: dict[str, Any] = {}
    with open(config_file, 'r') as fp_:
        loaded_config_content = yaml.load(fp_, Loader=UnsafeLoader)
    config = recursive_dict_update(config, loaded_config_content)

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
