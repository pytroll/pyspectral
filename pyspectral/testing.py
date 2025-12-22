"""Utilities for users writing tests that interact with Pyspectral."""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Callable
from unittest import mock

import numpy as np

from pyspectral.rsr_reader import RSRDict
from pyspectral.utils import ATMOSPHERES, RSR_DATA_VERSION, RSR_DATA_VERSION_FILENAME

TMP_LUT_BASE_DIR = Path(tempfile.gettempdir()) / "pyspectral_fake_luts"
BASE_RAYLEIGH_LUT_FILENAME = "base_fake_rayleigh_lut.h5"


@contextlib.contextmanager
def mock_pyspectral_downloads(
    tmp_path: Path = TMP_LUT_BASE_DIR,
    rsr_data_version: str = RSR_DATA_VERSION,
    extra_config_options: dict | None = None,
    central_wavelengths: dict[str, float] | None = None,
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
        mock.patch(
            "pyspectral.utils._download_tarball_and_extract"
        ) as download_tarball,
        override_config(config_options=config_options),
        mock_rayleigh_luts(rayleigh_dir, mock_config=False),
        mock.patch("pyspectral.rsr_reader._load_rsr_info_from_file") as load_rsr,
    ):
        download_tarball.side_effect = _fake_download
        load_rsr.side_effect = _fake_rsr_info_factory(
            central_wavelengths=central_wavelengths
        )
        # give the user the opportunity to customize the side effects
        yield {
            "download_tarball": download_tarball,
            "load_rsr_info": load_rsr,
        }


@contextlib.contextmanager
def mock_rayleigh_luts(
    rayleigh_dir: Path, existing_version: bool | str = True, mock_config: bool = True,
) -> Iterator[None]:
    """Mock the rayleigh LUT directories.

    Args:
        rayleigh_dir: Path where rayleigh LUTs should be created.
        existing_version: How to prepare the fake LUT directory. This can be
        ``True`` (default) meaning the directory should be created as if
        they are the most up-to-date versions of the LUTs. If ``False`` then
        the version and LUT files are not created beforehand and will be
        created as downloads are requested. Downloads are mocked so no
        internet connection is accessed.
        If a string value is provided then that will be used as the version
        of the LUT files (ex. 'v0.0.0' to represent out-of-date files).
        Note that a "template" HDF5 will be
        created in the root of the rayleigh directory so it can be linked to
        in any later LUT creation instead of creating a new LUT file every time.
        mock_config: Whether to include mocking pyspectral's config with the
        location of the rayleigh directory. Defaults to ``True``. If this is
        set to ``False`` then :func:`override_config` must be used to specify
        the ``rayleigh_dir`` provided to this function or pyspectral won't find
        the created LUTs.

    """
    from pyspectral.utils import AEROSOL_TYPES

    # TODO: Optional config override
    # TODO: Add existing data to replace what's in test_rayleigh.py
    _create_fake_rayleigh_file(rayleigh_dir / BASE_RAYLEIGH_LUT_FILENAME, "fake")

    if existing_version:
        # True==up-to-date else custom version
        _init_rayleigh_version_files(rayleigh_dir, existing_version)

        for aerosol_type in AEROSOL_TYPES:
            atype_subdir = rayleigh_dir / aerosol_type
            atype_subdir.mkdir(exist_ok=True)
            for atmo_name in ATMOSPHERES:
                atmo = atmo_name.replace(" ", "_")
                rayl_fn = f"rayleigh_lut_{atmo}.h5"
                rayl_path = atype_subdir / rayl_fn
                _symlink_rayleigh_lut(rayl_path)

    fake_config = {
        "rayleigh_dir": str(rayleigh_dir),
        "rsr_dir": str(rayleigh_dir),  # XXX: Correct?
        "download_from_internet": True,
    }
    config_cm = contextlib.nullcontext() if not mock_config else override_config(fake_config)
    with config_cm:
        yield


@contextlib.contextmanager
def _mock_download() -> Iterator[mock.Mock]:
    with mock.patch("pyspectral.utils._download_tarball_and_extract") as download_tarball:
        download_tarball.side_effect = _fake_download
        yield download_tarball


def _init_rayleigh_version_files(
    rayleigh_dir: Path, existing_version: bool | str
) -> None:
    from pyspectral.utils import AEROSOL_TYPES, ATM_CORRECTION_LUT_VERSION

    for aerosol_type in AEROSOL_TYPES:
        atype_version_fn = ATM_CORRECTION_LUT_VERSION[aerosol_type]["filename"]
        atype_version = ATM_CORRECTION_LUT_VERSION[aerosol_type]["version"]
        atype_subdir = rayleigh_dir / aerosol_type
        atype_subdir.mkdir(exist_ok=True)
        version_filename = str(atype_subdir / atype_version_fn)
        if isinstance(existing_version, str):
            atype_version = existing_version
        with open(version_filename, "w") as version_file:
            version_file.write(atype_version)


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
        try:
            yield config_path
        finally:
            if old_config_env is None:
                del os.environ["PSP_CONFIG_FILE"]
            else:
                os.environ["PSP_CONFIG_FILE"] = old_config_env


def _fake_download(
    tarball_url: str, tarball_local_path: str | Path, extract_dir: str | Path
) -> None:
    del tarball_url  # unused in this mocked version

    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    if tarball_local_path.name.endswith("rayleigh_correct_luts.tgz"):
        for atmo_name in ATMOSPHERES:
            atmo = atmo_name.replace(" ", "_")
            rayl_fn = f"rayleigh_lut_{atmo}.h5"
            rayl_path = extract_dir / rayl_fn
            if rayl_path.exists():
                continue
            _symlink_rayleigh_lut(rayl_path)
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


def _symlink_rayleigh_lut(link_path: Path) -> None:
    if link_path.exists():
        return

    rayleigh_dir = link_path.parent.parent
    base_file = rayleigh_dir / BASE_RAYLEIGH_LUT_FILENAME
    link_path.symlink_to(base_file)


def _fake_rsr_info_factory(
    central_wavelengths: dict[str, float] | None = None,
) -> Callable:
    if central_wavelengths is None:
        central_wavelengths = {}

    def _create_fake_rsr_info(rsr_path: Path) -> dict:
        from pyspectral.bandnames import BANDNAMES

        parts = rsr_path.stem.split("_")
        instrument = parts[1]
        platform_name = parts[2]
        if instrument.startswith("avhrr"):
            instrument = "avhrr/" + instrument[-1]
        band_name_map = BANDNAMES.get(
            instrument.lower().replace("/", "-"), BANDNAMES["generic"]
        )
        band_names = list(band_name_map.values())
        rsr_info = {
            "platform_name": platform_name,
            "instrument": instrument,
            "description": f"Relative Response for {instrument}",
            "band_names": band_names,
            "rsr": RSRDict(instrument),
        }
        central_wvl_map = RSRDict(instrument)
        for band_name, cwvl in central_wavelengths.items():
            # map user name to pyspectral "standard" name
            new_band_name = band_name_map.get(band_name, band_name)
            central_wvl_map[new_band_name] = cwvl
        response = np.linspace(0.0009, 1.0, 1000, dtype=np.float32)
        wvl = np.linspace(-0.02, 0.02, 1000, dtype=np.float32)
        for band_name in band_names:
            central_wvl = central_wvl_map.get(band_name, 0.46)
            rsr_info["rsr"][band_name] = {
                "det-1": {
                    "wavelength": wvl + central_wvl,
                    "central_wavelength": central_wvl,
                    "response": response,
                }
            }
        return rsr_info

    return _create_fake_rsr_info


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

    Note if you need some tests to not use this limitation (ex. tests that
    only run outside of CI) then the fixture can't be session scoped. See
    pyspectral's own ``pyspectral/tests/conftest.py`` for an example of using
    a pytest mark to control when tests are allowed to access downloads.

    """
    with mock.patch("pyspectral.utils.requests") as mock_requests:
        mock_requests.get.side_effect = RuntimeError(
            "Pyspectral is attempting a download during tests. Mock pyspectral as necessary to avoid this. "
            "See 'pyspectral.testing' for pyspectral-provided mocking functionality. This message is "
            "configured via a context manager likely being used from a 'your_pkg/tests/conftest.py' "
            "fixture."
        )
        yield
