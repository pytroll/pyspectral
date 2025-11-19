"""Utilities for users writing tests that interact with Pyspectral."""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import numpy as np

from pyspectral.utils import ATMOSPHERES, RSR_DATA_VERSION, RSR_DATA_VERSION_FILENAME

TMP_LUT_BASE_DIR = Path(tempfile.gettempdir()) / "pyspectral_fake_luts"


@contextlib.contextmanager
def mock_pyspectral_downloads(
    tmp_path: Path = TMP_LUT_BASE_DIR,
    rsr_data_version: str = RSR_DATA_VERSION,
    extra_config_options: dict | None = None,
):
    """Mock pyspectral's LUT downloads with fake realistic files."""
    config_options = {}
    # we want the tests to try to download files and create fake ones when that happens
    config_options["download_from_internet"] = True

    rsr_dir = tmp_path / "fake_rsr"
    rsr_dir.mkdir(parents=True, exist_ok=True)
    rayleigh_dir = tmp_path / "fake_rayleigh"
    rayleigh_dir.mkdir(parents=True, exist_ok=True)
    tb2rad_dir = tmp_path / "fake_tb2rad"
    tb2rad_dir.mkdir(parents=True, exist_ok=True)
    config_options["rsr_dir"] = str(rsr_dir)
    config_options["rayleigh_dir"] = str(rayleigh_dir)
    config_options["tb2rad_dir"] = str(tb2rad_dir)

    if extra_config_options:
        config_options.update(extra_config_options)

    # setup rsr directory
    rsr_version_path = rsr_dir / RSR_DATA_VERSION_FILENAME
    with rsr_version_path.open("w") as rsr_version_file:
        # defaults to active version, no downloading
        rsr_version_file.write(rsr_data_version)

    with (
        mock.patch("pyspectral.utils._download_tarball_and_extract") as download_tarball,
        override_config(config_options=config_options),
        mock.patch("pyspectral.rsr_reader._load_rsr_info_from_file") as load_rsr,
    ):
        download_tarball.side_effect = _fake_download
        load_rsr.side_effect = _create_fake_rsr_info
        # give the user the opportunity to customize the side effects
        yield {
            "download_tarball": download_tarball,
            "load_rsr_info": load_rsr,
        }


@contextlib.contextmanager
def override_config(config_options: dict | None = None) -> Iterator[Path]:
    """Override builtin config with temporary on-disk YAML file."""
    import yaml

    old_config_env = os.getenv("PSP_CONFIG_FILE", None)

    if config_options is None:
        config_options = {}

    with tempfile.TemporaryDirectory(prefix="fake_pyspectral_config_") as tmpdir:
        config_path = Path(tmpdir) / "pyspectral.yaml"
        with config_path.open("w") as config_file:
            yaml.dump(config_options, config_file)

        os.environ["PSP_CONFIG_FILE"] = str(config_path)
        yield config_path

    if old_config_env is None:
        del os.environ["PSP_CONFIG_FILE"]
    else:
        os.environ["PSP_CONFIG_FILE"] = old_config_env


def _fake_download(
    tarball_url: str, tarball_local_path: str | Path, extract_dir: str | Path
) -> None:
    print(tarball_url, tarball_local_path, extract_dir)
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
        raise NotImplementedError("Fake RSR creation is not implemented at this time")


def _create_fake_rayleigh_file(rayl_path: Path, atmo_name: str) -> None:
    import h5py

    with h5py.File(rayl_path, "w") as h:
        h.info = "Fake pyspectral rayleigh LUT file"
        h.create_dataset(
            "azimuth_difference", data=np.linspace(0.0, 180.0, 19, dtype=np.float64)
        )
        # NOTE: Create constant correction for each wavelength
        refl_data = np.repeat(
            np.repeat(
                np.repeat(
                    np.linspace(0.668, 0.115, 81, dtype=np.float64)[
                        :, np.newaxis, np.newaxis, np.newaxis
                    ],
                    96,
                    axis=1,
                ),
                19,
                axis=2,
            ),
            9,
            axis=3,
        )
        refl_var = h.create_dataset("reflectance", data=refl_data)
        setattr(refl_var, "1-axis", "wavelength")
        setattr(refl_var, "2-axis", "sun zenith secant")
        setattr(refl_var, "3-axis", "azimuth difference angle")
        setattr(refl_var, "4-axis", "satellite zenith secant")
        refl_var.atmosphere = atmo_name
        h.create_dataset(
            "satellite_zenith_secant", data=np.linspace(1.0, 3.0, 9, dtype=np.float64)
        )
        h.create_dataset(
            "sun_zenith_secant", data=np.linspace(1.0, 24.75, 96, dtype=np.float64)
        )
        h.create_dataset(
            "wavelengths", data=np.linspace(400, 800, 81, dtype=np.float64)
        )


def _create_fake_rsr_info(rsr_file: Path) -> dict:
    parts = rsr_file.name.split("_")
    instrument = parts[1]
    platform_name = parts[2]
    return {
        "instrument": instrument,
        "platform_name": platform_name,
        "description": f"Relative Response for {instrument}",
        "band_names": [],
        "rsr": {},
    }


class _FakeRSRDict(dict):

    def __getitem__(self, key):
        """Get RSR information dynamically and generate anything that is asked for."""
        print(f"Trying to access RSR for band {key}")
        return dict.__getitem__(self, key)


def _create_fake_rsr_files(rsr_path: Path, instrument: str, platform: str) -> None:
    import h5py

    from pyspectral.bandnames import BANDNAMES

    fn = f"rsr_{instrument}_{platform}.h5"
    base_file_path = rsr_path / fn
    if base_file_path.exists():
        return

    band_names = BANDNAMES.get(
        instrument.lower().replace("/", "-"), BANDNAMES["generic"]
    )
    response = np.linspace(0.0009, 1.0, 1000, dtype=np.float32)
    wvl = np.linspace(0.44, 0.5, 1000, dtype=np.float32)
    with h5py.File(base_file_path, "w") as h:
        h.band_names = band_names
        h.description = f"Relative Response for {instrument}"
        h.platform_name = platform

        for band_name in band_names:
            band_group = h.create_group(band_name)
            band_group.central_wavelength = 1.5  # TODO
            band_group.create_dataset("response", data=response)
            wvl_ds = band_group.create_dataset("wavelength", data=wvl)
            wvl_ds.scale = 1e-6
            wvl_ds.unit = "m"


def cleanup_fake_luts():
    """Clean up any fake LUT directories and files that were created."""
    shutil.rmtree(TMP_LUT_BASE_DIR)


@contextlib.contextmanager
def forbid_pyspectral_downloads():
    """Raise exception if pyspectral tries to download LUTs from the internet.

    It is recommended to add this to your package's tests' root ``conftest.py``
    as a session-level autouse fixture. For example:

    .. code-block:: python

        from pyspectral.testing import forbid_pyspectral_downloads

        @pytest.fixture(autouse=True, scope="session")
        def _forbid_pyspectral_downloads():
            with forbid_pyspectral_downloads():
                yield

    To avoid errors caused by this context manager, mocking or other fake data
    creation should be used to avoid pyspectral attempting a download. See the
    other context managers and functions in ``pyspectral.testing`` for available
    pyspectral-provided functionality.

    """
    with mock.patch("pyspectral.utils.requests") as mock_requests:
        mock_requests.get.side_effect = RuntimeError(
            "Pyspectral is attempting a download during tests. Mock pyspectral as necessary to avoid this. "
            "See 'pyspectral.testing' for pyspectral-provided mocking functionality. This message is "
            "configured via a context manager likely being used from a 'your_pkg/tests/conftest.py' "
            "fixture.")
        yield
