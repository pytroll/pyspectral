"""Utilities for writing third-party tests that interact with Pyspectral.

The :mod:`pyspectral.testing` module provides functionality primarily for
users of pyspectral to add to their own testing. By using these utilities
you can avoid downloading pyspectral LUTs and other files that pyspectral
may want to download. This should make your tests faster and require less
disk space while also making your CI runners and pyspectral's data host
happier due to fewer (or no) downloads.

There are two levels of utilities. High-level utilities are most useful
and typically mock a single component/interface of Pyspectral. Lower-level
utilities are used by the higher-level utilities and generally only handle
one part of the necessary changes to avoid Pyspectral downloads. For example,
a low-level utility may set up the environment to create fake LUT files, but
won't set up the Pyspectral configuration to make Pyspectral use those files.
Unless you are trying to optimize how and when the mocking is performed, it
is recommended to use the high-level utilities.

Pytest fixtures
^^^^^^^^^^^^^^^

Many of these utilities are context managers. If using these functions
from pytest-based unit tests, it can be a good idea, although not required,
to make a pytest fixture and pass pytest's `tmp_path` to the utilities that
require a directory. For example:

.. code-block::

   @pytest.mark.fixture
   def fake_pyspectral(tmp_path):
       from pyspectral.testing import mock_pyspectral_downloads

       with mock_pyspectral_downloads(tmp_path=tmp_path):
           yield

This is especially useful for utilities like :func:`forbid_pyspectral_downloads`
which can be set to run at the start of the pytest session and apply to all
tests. See the individual function API documentation for examples.

High-level utilities
^^^^^^^^^^^^^^^^^^^^

* :func:`mock_pyspectral_downloads`
* :func:`mock_tb_conversion`
* :func:`mock_rsr`
* :func:`mock_rayleigh`
* :func:`override_config`
* :func:`forbid_pyspectral_downloads`

See the API documentation linked above for more information on how to use
these functions.

Lower-level utilities
^^^^^^^^^^^^^^^^^^^^^

* :func:`init_tb_cache`
* :func:`mock_rsr_files`
* :func:`mock_rayleigh_luts`

"""

from __future__ import annotations

import contextlib
import os
import tempfile
from collections.abc import Iterable, Iterator
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Callable
from unittest import mock

import numpy as np

from pyspectral.rsr_reader import RSRDict
from pyspectral.utils import (
    AEROSOL_TYPES,
    ATMOSPHERES,
    RSR_DATA_VERSION,
    RSR_DATA_VERSION_FILENAME,
)

BASE_RAYLEIGH_LUT_FILENAME = "base_fake_rayleigh_lut.h5"


@contextlib.contextmanager
def mock_pyspectral_downloads(
    *,
    tmp_path: Path | None = None,
    extra_config_options: dict | None = None,
    rsr_files_kwargs: dict | None = None,
) -> Iterator[None]:
    """Mock pyspectral's interfaces to avoid downloading files from the internet.

    This currently mocks and creates fakes versions of Rayleigh LUTs, RSR
    files, and the TB2Rad cache. It also overrides
    the pyspectral global configuration file to use these fake files.
    This function is an all-in-one version of the other high-level testing
    mocking utilities.

    Args:
        tmp_path: Base directory to create fake files. If not provided
            or None, a directory will be created when the context manager is
            entered and deleted when exited. If provided, the directory and its
            contents will not be deleted.
        extra_config_options: Extra pyspectral configuration settings to set
            in addition to those required for mocking to succeed.
        rsr_files_kwargs: Keyword arguments to pass to :func:`mock_rsr_files`.

    """
    tmp_path_manager = None
    if tmp_path is None:
        tmp_path_manager = tempfile.TemporaryDirectory(prefix="pyspectral_testing_")
        tmp_path = tmp_path_manager.name

    config_options = {}
    config_options["download_from_internet"] = False

    rsr_dir = tmp_path / "fake_rsr"
    rayleigh_dir = tmp_path / "fake_rayleigh"
    tb2rad_dir = tmp_path / "fake_tb2rad"
    config_options["rsr_dir"] = str(rsr_dir)
    config_options["rayleigh_dir"] = str(rayleigh_dir)
    config_options["tb2rad_dir"] = str(tb2rad_dir)

    if extra_config_options:
        config_options.update(extra_config_options)
    rsr_files_kwargs = rsr_files_kwargs or {}

    with (
        override_config(config_options=config_options),
        mock_rayleigh_luts(rayleigh_dir=rayleigh_dir),
        init_tb_cache(tb2rad_dir),
        mock_rsr_files(rsr_dir, **rsr_files_kwargs),
    ):
        yield
    # NOTE: Temporary directory created by tempfile is deleted on garbage collection
    del tmp_path_manager


@contextlib.contextmanager
def mock_tb_conversion(
    *, tb2rad_dir: Path | None = None, rsr_dir: Path | None = None, **rsr_files_kwargs
) -> Iterator[mock.Mock]:
    """Mock pyspectral to avoid downloads and caching for Calculator and RadTbConverter classes.

    Args:
        tb2rad_dir: Path to store Tb to radiance LUT data. If not provided
            a temporary one will be used and deleted on exit of the context manager.
        rsr_dir: Path to store fake RSR files. If not provided then the
            ``tb2rad_dir`` will be used.
        rsr_files_kwargs: Keyword arguments to pass to :func:`mock_rsr_files`.

    """
    tmp_path_manager = None
    if tb2rad_dir is None:
        tmp_path_manager = tempfile.TemporaryDirectory(prefix="pyspectral_testing_")
        tb2rad_dir = tmp_path_manager.name
    if rsr_dir is None:
        rsr_dir = tb2rad_dir

    fake_config = {
        "rsr_dir": str(rsr_dir),
        "tb2rad_dir": str(tb2rad_dir),
        "download_from_internet": False,
    }
    config_cm = override_config(config_options=fake_config)
    rsr_files_cm = mock_rsr_files(
        rsr_dir,
        **rsr_files_kwargs,
    )
    with config_cm, rsr_files_cm as load_rsr:
        yield load_rsr

    # NOTE: Temporary directory created by tempfile is deleted on garbage collection
    del tmp_path_manager


@contextlib.contextmanager
def init_tb_cache(tb2rad_dir: Path) -> Iterator[None]:
    """Initialize RadTbConverter and Calculator cache directory.

    It will be filled when tests call the necessary methods of the effected classes.
    """
    tb2rad_dir.mkdir(parents=True, exist_ok=True)
    yield


@contextlib.contextmanager
def mock_rsr(
    *,
    rsr_dir: Path | None = None,
    rsr_data_version: str = RSR_DATA_VERSION,
    central_wavelengths: dict[str, float] | None = None,
    side_effect: Any = "__unset__",
    return_value: Any = "__unset__",
) -> Iterator[mock.Mock]:
    """Mock the RelativeSpectralResponse class to avoid download of RSR files.

    This is the high-level function that uses `mock_rsr_files` to do the
    work of creating fake RSR files and mocking the necessary parts of pyspectral.
    Additionally, this function overrides the global pyspectral config file to
    allow the fake RSR files to be used.

    Args:
        rsr_dir: Path to store fake RSR files. If not provided then a
            temporary directory is used and deleted on exit of the context manager.
        rsr_data_version: Version number to use for the created fake RSR files.
            By default, the newest/active version number will be used.
        central_wavelengths: Dictionary mapping a channel name to a central wavelength
            floating point number. This is used to generate more realistic data in the
            created fake RSR files. This has no effect if ``side_effect`` or
            ``return_value`` are specified.
        side_effect: Force the mocking of the data coming from the fake files.to use
            this callback or exception class. This is a low-level option and typically
            does not need to be specified. This has no effect if ``return_value`` is
            specified.
        return_value: Force the mocking of the data coming from the fake file to be
            exactly this value. This is a low-level option and typically does not need
            to be specified. This value takes priority over ``side_effect`` and
            ``central_wavelengths``.

    """
    tmp_path_manager = None
    if rsr_dir is None:
        tmp_path_manager = tempfile.TemporaryDirectory(prefix="pyspectral_testing_")
        rsr_dir = tmp_path_manager.name
    fake_config = {
        "rsr_dir": str(rsr_dir),
        "download_from_internet": False,
    }
    config_cm = override_config(config_options=fake_config)
    rsr_files_cm = mock_rsr_files(
        rsr_dir,
        rsr_data_version=rsr_data_version,
        central_wavelengths=central_wavelengths,
        side_effect=side_effect,
        return_value=return_value,
    )
    with config_cm, rsr_files_cm as load_rsr:
        yield load_rsr
    # NOTE: Temporary directory created by tempfile is deleted on garbage collection
    del tmp_path_manager


@contextlib.contextmanager
def mock_rsr_files(
    rsr_dir: Path,
    *,
    rsr_data_version: str = RSR_DATA_VERSION,
    central_wavelengths: dict[str, float] | None = None,
    side_effect: Any = "__unset__",
    return_value: Any = "__unset__",
) -> Iterator[mock.Mock]:
    """Mock the RelativeSpectralResponse class and create fake RSR files to avoid downloads.

    This function does not override the pyspectral global configuration and as such
    the modifications applied by this function do not completely mock all access to
    RSR files. You must either use the higher-level `mock_rsr` function instead or override
    the configuration yourself using `override_config` and set ``rsr_dir`` to the
    path passed to this function.

    Args:
        rsr_dir: Path to store fake RSR files.
        rsr_data_version: Version number to use for the created fake RSR files.
            By default, the newest/active version number will be used.
        central_wavelengths: Dictionary mapping a channel name to a central wavelength
            floating point number. This is used to generate more realistic data in the
            created fake RSR files. This has no effect if ``side_effect`` or
            ``return_value`` are specified.
        side_effect: Force the mocking of the data coming from the fake files.to use
            this callback or exception class. This is a low-level option and typically
            does not need to be specified. This has no effect if ``return_value`` is
            specified.
        return_value: Force the mocking of the data coming from the fake file to be
            exactly this value. This is a low-level option and typically does not need
            to be specified. This value takes priority over ``side_effect`` and
            ``central_wavelengths``.

    """
    rsr_dir.mkdir(parents=True, exist_ok=True)

    rsr_version_path = rsr_dir / RSR_DATA_VERSION_FILENAME
    with rsr_version_path.open("w") as rsr_version_file:
        # defaults to active version, no downloading
        rsr_version_file.write(rsr_data_version)

    with mock.patch("pyspectral.rsr_reader._load_rsr_info_from_file") as load_rsr:
        if return_value != "__unset__":
            load_rsr.return_value = return_value
        elif side_effect != "__unset__":
            load_rsr.side_effect = side_effect
        else:
            load_rsr.side_effect = _fake_rsr_info_factory(
                central_wavelengths=central_wavelengths
            )

        yield load_rsr


@contextlib.contextmanager
def mock_rayleigh(
    *,
    rayleigh_dir: Path | None = None,
    rsr_dir: Path | None = None,
    existing_version: bool | str = True,
    lut_data: dict | None = None,
    aerosol_types: Iterable[str] | None = None,
    atmospheres: Iterable[str] | None = None,
) -> Iterator[None]:
    """Mock the Rayleigh interfaces to avoid LUT downloads.

    This high-level function overrides the pyspectral configuration
    and creates fake rayleigh LUT files using `mock_rayleigh_luts`.

    Args:
        rayleigh_dir: Path where rayleigh LUTs should be created.
            If not specified then a temporary directory will be created and
            deleted on exit of the context manager.
        rsr_dir: Path to store fake RSR files. If not specified then this is
            set to ``rayleigh_dir``.
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
        lut_data: Dictionary of numpy arrays to store to the HDF5 LUT file.
            Keys must include "azimuth_difference", "reflectance",
            "satellite_zenith_secant", "sun_zenith_secant", and "wavelengths".
        aerosol_types: List of aerosol types to create files for. Defaults to
            all supported types.
        atmospheres: Atmospheres to create LUTs for. Defaults to all supported
            atmosphere types.
    """
    tmp_path_manager = None
    if rayleigh_dir is None:
        tmp_path_manager = tempfile.TemporaryDirectory(prefix="pyspectral_testing_")
        rayleigh_dir = tmp_path_manager.name

    if rsr_dir is None:
        rsr_dir = rayleigh_dir
    fake_config = {
        "rayleigh_dir": str(rayleigh_dir),
        "rsr_dir": str(rsr_dir),
        "download_from_internet": False,
    }
    config_cm = override_config(config_options=fake_config)
    luts_cm = mock_rayleigh_luts(
        rayleigh_dir=rayleigh_dir,
        existing_version=existing_version,
        lut_data=lut_data,
        aerosol_types=aerosol_types,
        atmospheres=atmospheres,
    )
    rsr_files_cm = mock_rsr_files(rsr_dir)
    with config_cm, luts_cm, rsr_files_cm:
        yield
    # NOTE: Temporary directory created by tempfile is deleted on garbage collection
    del tmp_path_manager


@contextlib.contextmanager
def mock_rayleigh_luts(
    rayleigh_dir: Path,
    *,
    existing_version: bool | str = True,
    lut_data: dict | None = None,
    aerosol_types: Iterable[str] | None = None,
    atmospheres: Iterable[str] | None = None,
) -> Iterator[None]:
    """Mock the rayleigh LUT directories.

    Note this function does not mock the pyspectral global configuration necessary
    for the fake rayleigh LUTs to be used by pyspectral. You must either use
    :func:`mock_rayleigh` instead or use :func:`override_config` to override
    the configuration yourself and call :func:`mock_rsr_files` to mock the RSR
    files used by the Rayleigh class. The new configuration data must include
    ``rayleigh_dir`` passed to this function and ``rsr_dir`` passed to the
    :func:`mock_rsr_files` function.

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
        lut_data: Dictionary of numpy arrays to store to the HDF5 LUT file.
            Keys must include "azimuth_difference", "reflectance",
            "satellite_zenith_secant", "sun_zenith_secant", and "wavelengths".
        aerosol_types: List of aerosol types to create files for. Defaults to
            all supported types.
        atmospheres: Atmospheres to create LUTs for. Defaults to all supported
            atmosphere types.

    """
    if aerosol_types is None:
        aerosol_types = AEROSOL_TYPES
    if atmospheres is None:
        atmospheres = ATMOSPHERES

    rayleigh_dir.mkdir(parents=True, exist_ok=True)
    _create_fake_rayleigh_file(
        rayleigh_dir / BASE_RAYLEIGH_LUT_FILENAME, "fake", lut_data
    )

    if existing_version:
        # True==up-to-date else custom version
        _init_rayleigh_version_files(rayleigh_dir, existing_version, aerosol_types)

        for aerosol_type in aerosol_types:
            atype_subdir = rayleigh_dir / aerosol_type
            atype_subdir.mkdir(exist_ok=True)
            for atmo_name in atmospheres:
                atmo = atmo_name.replace(" ", "_")
                rayl_fn = f"rayleigh_lut_{atmo}.h5"
                rayl_path = atype_subdir / rayl_fn
                _symlink_rayleigh_lut(rayl_path)

    yield


def _init_rayleigh_version_files(
    rayleigh_dir: Path,
    existing_version: bool | str,
    aerosol_types: Iterable[str],
) -> None:
    from pyspectral.utils import ATM_CORRECTION_LUT_VERSION

    for aerosol_type in aerosol_types:
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
def override_config(
    config_options: dict | None = None, config_path: Path | None = None
) -> Iterator[Path]:
    """Override builtin config with temporary on-disk YAML file."""
    old_config_env = os.getenv("PSP_CONFIG_FILE", None)

    config_path_cm = (
        nullcontext(config_path)
        if config_path is not None
        else _create_temp_rayleigh_config_file(config_options)
    )

    with config_path_cm as config_path:
        os.environ["PSP_CONFIG_FILE"] = str(config_path)
        try:
            yield config_path
        finally:
            if old_config_env is None:
                del os.environ["PSP_CONFIG_FILE"]
            else:
                os.environ["PSP_CONFIG_FILE"] = old_config_env


@contextlib.contextmanager
def _create_temp_rayleigh_config_file(
    config_options: dict | None = None,
) -> Iterator[Path]:
    with _pyspectral_temp_config_path() as config_path:
        create_pyspectral_config_file(config_path, config_options=config_options)
        yield config_path


def create_pyspectral_config_file(
    config_path: Path, config_options: dict | None = None
) -> None:
    """Create an on-disk YAML file with the provided options.

    Args:
        config_path: Path of the config file to create.
        config_options: Configuration options to write to YAML file. If
            not provided then an empty dictionary is used.
    """
    import yaml

    if config_options is None:
        config_options = {}

    with config_path.open("w") as config_file:
        yaml.dump(config_options, config_file)


@contextlib.contextmanager
def _pyspectral_temp_config_path() -> Iterator[Path]:
    """Create temporary directory and get a YAML file location inside that directory.

    Windows doesn't like NamedTemporaryFile when things may be left open or cached.
    """
    with tempfile.TemporaryDirectory(prefix="fake_pyspectral_config_") as tmpdir:
        yield Path(tmpdir) / "pyspectral.yaml"


def _create_fake_rayleigh_file(
    rayl_path: Path, atmo_name: str, lut_data: dict | None = None
) -> None:
    import h5py

    if lut_data is None:
        lut_data = _default_rayleigh_lut_data()

    dtype = np.float64
    with h5py.File(rayl_path, "w") as h:
        h.info = "Fake pyspectral rayleigh LUT file"
        h.create_dataset(
            "azimuth_difference", data=lut_data["azimuth_difference"].astype(dtype)
        )
        refl_var = h.create_dataset(
            "reflectance", data=lut_data["reflectance"].astype(dtype)
        )
        setattr(refl_var, "1-axis", "wavelength")
        setattr(refl_var, "2-axis", "sun zenith secant")
        setattr(refl_var, "3-axis", "azimuth difference angle")
        setattr(refl_var, "4-axis", "satellite zenith secant")
        refl_var.atmosphere = atmo_name
        h.create_dataset(
            "satellite_zenith_secant",
            data=lut_data["satellite_zenith_secant"].astype(dtype),
        )
        h.create_dataset(
            "sun_zenith_secant", data=lut_data["sun_zenith_secant"].astype(dtype)
        )
        h.create_dataset("wavelengths", data=lut_data["wavelengths"].astype(dtype))


def _default_rayleigh_lut_data() -> dict:
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
    return {
        "azimuth_difference": np.linspace(0.0, 180.0, 19, dtype=np.float64),
        "reflectance": refl_data,
        "wavelengths": np.linspace(400, 800, 81, dtype=np.float64),
        "satellite_zenith_secant": np.linspace(1.0, 3.0, 9, dtype=np.float64),
        "sun_zenith_secant": np.linspace(1.0, 24.75, 96, dtype=np.float64),
    }


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
