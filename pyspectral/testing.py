"""Utilities for users writing tests that interact with Pyspectral."""
from __future__ import annotations

import contextlib
import shutil
import tempfile
from pathlib import Path
from unittest import mock

TMP_LUT_BASE_DIR = Path(tempfile.gettempdir()) / "pyspectral_fake_luts"


@contextlib.contextmanager
def mock_pyspectral_downloads(tmp_path: Path = TMP_LUT_BASE_DIR):
    """Mock pyspectral's LUT downloads with fake realistic files."""
    from pyspectral.config import get_config

    # TODO: Call this once when we enter the mocking (separate function?) then
    #    set `get_config.return_value` instead of `side_effect`.
    def _force_fake_lut_dirs():
        config = get_config()

        rsr_dir = tmp_path / "fake_rsr"
        rsr_dir.mkdir(parents=True, exist_ok=True)
        rayleigh_dir = tmp_path / "fake_rayleigh"
        rayleigh_dir.mkdir(parents=True, exist_ok=True)
        tb2rad_dir = tmp_path / "fake_tb2rad"
        tb2rad_dir.mkdir(parents=True, exist_ok=True)
        config["rsr_dir"] = str(rsr_dir)
        config["rayleigh_dir"] = str(rayleigh_dir)
        config["tb2rad_dir"] = str(tb2rad_dir)

        return config

    with mock.patch("pyspectral.utils._download_tarball_and_extract") as download_tarball_and_extract:
        download_tarball_and_extract.side_effect = _fake_download
        # TODO: Replace get_config mocking with overwritten config file
        # TODO: Also set download_from_internet to False?
        with mock.patch("pyspectral.utils.get_config") as get_config1, \
                mock.patch("pyspectral.near_infrared_reflectance.get_config") as get_config2:
            get_config1.side_effect = _force_fake_lut_dirs
            get_config2.side_effect = _force_fake_lut_dirs
            yield


def _fake_download(tarball_url: str, tarball_local_path: str | Path, extract_dir: str | Path) -> None:
    print(tarball_url, tarball_local_path, extract_dir)


def cleanup_fake_luts():
    """Clean up any fake LUT directories and files that were created."""
    shutil.rmtree(TMP_LUT_BASE_DIR)
