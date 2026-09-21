# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Pyspectral (pytroll) reads satellite imager relative spectral response (RSR) functions and
uses them for radiative calculations: solar flux per band, radiance<->brightness-temperature
conversion, 3.7 micron NIR reflectance separation, and Rayleigh/aerosol atmospheric
correction of VIS bands. It is a library, mainly consumed by Satpy; there is no application
entry point, only the helper scripts in `bin/`.

## Commands

```bash
pip install -e .                       # development install (setuptools_scm writes pyspectral/version.py)
pytest pyspectral/tests                # full test suite
pytest pyspectral/tests/test_rayleigh.py::TestRayleigh::test_get_reflectance   # single test
pytest --cov=pyspectral pyspectral/tests --cov-report=xml                      # as CI runs it
pre-commit run -a                      # flake8 (+docstrings/debugger/bugbear) and isort
cd doc && make html                    # sphinx docs
```

Line length is 120 (flake8 and isort). flake8-docstrings is enabled, so every module,
class and function needs a docstring. Python >= 3.10; CI runs 3.10-3.12 on conda
environments built from `continuous_integration/environment.yaml`.

Missing test dependencies in this environment should be installed with
`micromamba install -p /opt/conda -c conda-forge <pkg>` (e.g. `responses`, needed by
`test_utils.py`).

PRs go against `pre-master`, not `main`.

## Architecture

### Data flow

Almost everything starts from `RelativeSpectralResponse` (`rsr_reader.py`), which loads a
sensor's RSR from Pyspectral's own unified HDF5 format into
`rsr[band_name][detector]{"wavelength", "response", "central_wavelength"}`. The HDF5 files
are *not* in the repository: they are downloaded on demand from Zenodo. The higher-level
calculators build on that:

- `solar.SolarIrradianceSpectrum` - TOA solar spectrum (`pyspectral/data/e490_00a.dat`),
  convolved with an RSR to get in-band solar flux.
- `radiance_tb_conversion.RadTbConverter` - RSR-weighted radiance <-> Tb using
  `blackbody.py` (Planck). `SeviriRadTbConverter` is a specialisation.
- `near_infrared_reflectance.Calculator` - subclasses `RadTbConverter`; splits the 3.7/3.9
  micron signal into solar and terrestrial parts. Caches a Tb<->radiance LUT as an `.npz`
  under `tb2rad_dir` (default: tempdir).
- `rayleigh.Rayleigh` - interpolates precomputed Rayleigh/aerosol LUTs (HDF5, per aerosol
  type and standard atmosphere) with `geotiepoints.MultilinearInterpolator`. LUTs are also
  downloaded from Zenodo.
- `atm_correction_ir.AtmosphericalCorrection` - old parametric limb-cooling correction.

### Configuration and downloaded data

`config.get_config()` reads `pyspectral/etc/pyspectral.yaml`, or the file pointed to by the
`PSP_CONFIG_FILE` environment variable. It resolves `rsr_dir` and `rayleigh_dir`, defaulting
to the platformdirs user data dir, and creates them. The same YAML doubles as the place
where users point the `rsr_convert_scripts/` at original agency RSR files (one section per
`<Platform>-<instrument>`), which is why it is so long.

Download behaviour is governed by `download_from_internet` in that YAML plus version
stamp files written next to the data: `RSR_DATA_VERSION` / `ATM_CORRECTION_LUT_VERSION` in
`utils.py` are compared against `PYSPECTRAL_RSR_VERSION` / `PYSPECTRAL_ATM_CORR_LUT_*` files
in the data dirs to decide whether to re-download. When RSR data on Zenodo is updated, bump
`RSR_DATA_VERSION` and `HTTP_PYSPECTRAL_RSR` together.

Zenodo is the default source but not the only one: `get_rsr_url()` / `get_rayleigh_lut_url()`
build the download URLs, and when a mirror is configured (`PSP_DATA_BASE_URL` environment
variable, or `download_base_url` in the YAML) they point at it instead, using the versioned
layout that `mirror_data()` and `bin/mirror_pyspectral_data.py` produce. Any new download
should go through those functions rather than reading a URL constant directly.

`utils.INSTRUMENTS` maps platform -> instrument(s) and is the authority on which
platform/sensor combinations exist; `check_and_adjust_instrument_name` and
`rayleigh.normalize_sensor` reconcile the several spellings in use (`avhrr-3` vs `avhrr/3`,
`mersi2` vs `mersi-2`). `bandnames.BANDNAMES` maps sensor-specific band names to the generic
names used internally, so most public APIs accept a band name *or* a wavelength in microns.

### Dask handling

Dask is an optional dependency, so modules do `try: import dask.array as da / except
ImportError`. Computational functions must work on plain numpy arrays, dask arrays and
xarray DataArrays alike. The `@use_map_blocks_on("<arg>")` decorator in `utils.py` is the
standard way to get that: it passes numpy straight through and wraps chunked input in
`da.map_blocks`, preserving the xarray wrapper.

### Tests and downloads

`pyspectral/tests/conftest.py` installs an autouse fixture that makes any download attempt
raise. A test that genuinely needs the network must be marked
`@pytest.mark.allow_downloads(use=True)`. Tests therefore work against fake RSR/LUT data
built by `pyspectral/testing.py`.

`pyspectral.testing` is public API, not test-only helpers: it exists so that downstream
projects (Satpy) can mock Pyspectral's downloads in their own test suites. It offers
high-level context managers (`mock_pyspectral_downloads`, `mock_rsr`, `mock_rayleigh`,
`mock_tb_conversion`) layered on lower-level ones that create fake files and override the
config. Keep it importable without test-only dependencies, and cover it in
`tests/test_testing.py`.

### rsr_convert_scripts/

One script per sensor, converting original agency RSR data (Excel, text, netCDF, ...) into
the unified HDF5 format, usually via `raw_reader.InstrumentRSR` plus `utils.convert2hdf5`.
These are excluded from coverage and are only run by maintainers when an agency publishes
updated responses; the result is uploaded to Zenodo rather than committed here.
