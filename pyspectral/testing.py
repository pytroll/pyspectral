"""Utilities for users writing tests that interact with Pyspectral."""
from __future__ import annotations

import contextlib
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np

from pyspectral.utils import ATMOSPHERES

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
    del tarball_url  # unused in this mocked version

    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    if "fake_rayleigh" in str(tarball_local_path):
        for atmo_name in ATMOSPHERES:
            rayl_fn = f"rayleigh_lut_{atmo_name}.h5"
            rayl_path = extract_dir / rayl_fn
            if rayl_path.exists():
                continue
            _create_fake_rayleigh_file(rayl_path, atmo_name)
    else:
        raise NotImplementedError("Only rayleigh LUT fake creation implemented at this time")


def _create_fake_rayleigh_file(rayl_path: Path, atmo_name: str) -> None:
    import h5py

    with h5py.File(rayl_path, "w") as h:
        h.info = "Fake pyspectral rayleigh LUT file"
        h.create_dataset("azimuth_difference", data=np.linspace(0.0, 180.0, 19, dtype=np.float64))
        # NOTE: Create constant correction for each wavelength
        refl_data = np.repeat(np.repeat(np.repeat(
            np.linspace(0.668, 0.115, 81, dtype=np.float64)[:, np.newaxis, np.newaxis, np.newaxis],
            96, axis=1), 19, axis=2), 9, axis=3)
        refl_var = h.create_dataset("reflectance", data=refl_data)
        setattr(refl_var, "1-axis", "wavelength")
        setattr(refl_var, "2-axis", "sun zenith secant")
        setattr(refl_var, "3-axis", "azimuth difference angle")
        setattr(refl_var, "4-axis", "satellite zenith secant")
        refl_var.atmosphere = atmo_name
        h.create_dataset("satellite_zenith_secant", data=np.linspace(1.0, 3.0, 9, dtype=np.float64))
        h.create_dataset("sun_zenith_secant", data=np.linspace(1.0, 24.75, 96, dtype=np.float64))
        h.create_dataset("wavelengths", data=np.linspace(400, 800, 81, dtype=np.float64))


def cleanup_fake_luts():
    """Clean up any fake LUT directories and files that were created."""
    shutil.rmtree(TMP_LUT_BASE_DIR)
