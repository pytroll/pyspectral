Changelog
=========

v0.7.0 (2018-04-17)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.6.5 → 0.7.0. [Adam.Dybbroe]

- Fix so that unitests pass silently and successfully at the end.
  [Adam.Dybbroe]

  On some Pythn systems we have seen that the unittests complain in the end
  with a "TypeError: 'NoneType' object is not callable" and an "Exception
  in thread"

- Merge pull request #33 from pytroll/feature_dask_atm_correction. [Adam
  Dybbroe]

  Fix Rayleigh corrector to work with dask

- Merge branch 'develop' into feature_dask_atm_correction.
  [Adam.Dybbroe]

- Bugfix OLCI band names. [Adam.Dybbroe]

- Fix h5pickle on 3.5 environments (not supported) [davidh-ssec]

- Add h5pickle if the python version is compatible. [davidh-ssec]

- Add h5pickle for safer HDF5 handling with dask in rayleigh correction.
  [davidh-ssec]

- Fix dask array requirement for tests. [davidh-ssec]

- Fix line too long. [davidh-ssec]

- Remove leftover print statements. [davidh-ssec]

- Fix rayleigh correction converting dask array to numpy. [davidh-ssec]

- Fix rayleigh correction to work with dask installed and numpy inputs.
  [davidh-ssec]

- Fix more style issues. [davidh-ssec]

- More style fixes. [davidh-ssec]

- More style fixes. [davidh-ssec]

- Fix a styling issues. [davidh-ssec]

- Add missing toolz dependency on CI environments. [davidh-ssec]

- Add dask to CI environments. [davidh-ssec]

- Fix rayleigh corrector to work with or without dask. [davidh-ssec]

- Fix flake8 style issues. [davidh-ssec]

- Update rayleigh correction to be better about using dask. [davidh-
  ssec]

- Daskifying: Keep the h5 lut-file open. [Adam.Dybbroe]

- First steps daskifying... [Adam.Dybbroe]

v0.6.5 (2018-03-31)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.6.4 → 0.6.5. [Adam.Dybbroe]

- Remove private test scripts from git. [Adam.Dybbroe]

v0.6.4 (2018-03-22)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.6.3 → 0.6.4. [Adam.Dybbroe]

- Slightly improved short and long readme descriptions. [Adam.Dybbroe]

- Increase test coverage. [Adam.Dybbroe]

- Mock unittest so it doesn't try downloading the RSR data.
  [Adam.Dybbroe]

- Get the updated dataset of atm correction LUTs (all in one zenodo
  dataset) [Adam.Dybbroe]

- Fix unittests. [Adam.Dybbroe]

- Check the version of the local RSR data, and if old download latest.
  [Adam.Dybbroe]

- Remove RSR data from git-repo. [Adam.Dybbroe]

  RSR data is donwloaded automagically from Zenodo when need by the user

- Make it possible to specify a custom base-path where radiance-tb LUTs
  are stored. [Adam.Dybbroe]

- Fix bug - straight wavelength bins in solar interpolation method.
  [Adam.Dybbroe]

- Fix doc tests for python3. [Adam.Dybbroe]

- Merge pull request #31 from michaelaye/fix_mpl_warning. [Adam Dybbroe]

  change pylab calls to OO pyplot calls. Fixes #30

- Remove obsolete add_subplot line. [K.-Michael Aye]

- Change pylab calls to OO pyplot calls. Fixes #30. [K.-Michael Aye]

v0.6.3 (2018-01-22)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.6.2 → 0.6.3. [Adam.Dybbroe]

- Merge pull request #27 from pytroll/feature-atmcorr-without-rsr. [Adam
  Dybbroe]

  Feature atmcorr without rsr

- Use us-standard atm and marine-clean aerosol distribution as the
  default. [Adam.Dybbroe]

- Fix atm correction example - update to use red band instead of blue
  band for reducing correction over strong reflectors. [Adam.Dybbroe]

- Improve documentation on atm correction. [Adam.Dybbroe]

- Vary the unit test cases a bit more - add greater spread in the indata
  between tests. [Adam.Dybbroe]

- Add unittest to verify that rayleigh correction can be done without
  RSR data. [Adam.Dybbroe]

- Merge pull request #25 from pytroll/landsat8. [Adam Dybbroe]

  Landsat-8

- Merge branch 'develop' into landsat8. [Adam.Dybbroe]

- Merge pull request #24 from pytroll/bugfix-olci. [Adam Dybbroe]

  Bugfix OLCI S3A. Add channel 21, rename bands and fix doc pages

- Bugfix OLCI S3A. Add channel 21, rename bands and fix doc pages.
  [Adam.Dybbroe]

- Fix flak8 issues. [Adam.Dybbroe]

- Merge branch 'develop' into landsat8. [Adam.Dybbroe]

- Merge pull request #23 from pytroll/sentinel2. [Adam Dybbroe]

  Sentinel-2

- Update zenodo link to new RSR archive, and update list of supported
  platforms. [Adam.Dybbroe]

- Fix flake8 complaints. [Adam.Dybbroe]

- Merge branch 'develop' into sentinel2. [Adam.Dybbroe]

- Add support for Sentinel 2 MSI RSR data. Further,
  get_bandname_from_wavelength now needs the sensor name as input.
  [Adam.Dybbroe]

- Add Sentinel-2 RSR. [Adam.Dybbroe]

- Add support for Landsat-8 OLI. [Adam.Dybbroe]

- Use the name PySpectral throughout. Improve documentation.
  [Adam.Dybbroe]

- Merge pull request #22 from pytroll/appveyor. [Adam Dybbroe]

  Appveyor

- Fixed unused imports and reuse parameters from utils.py.
  [Adam.Dybbroe]

- Comment out Appveyor tests for Py3.4. [Adam.Dybbroe]

- Fix OS independent file paths for unittests. [Adam.Dybbroe]

- Don't run doc tests in Appveyor. [Adam.Dybbroe]

- Get the system dependent tmp dir via tempfile module. [Adam.Dybbroe]

- Add Appveyor badge. [Adam.Dybbroe]

- Install python-geotiepoints from PyPI instead of with conda.
  [Adam.Dybbroe]

- Add for Appveyor. [Adam.Dybbroe]

v0.6.2 (2018-01-10)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.6.1 → 0.6.2. [Adam.Dybbroe]

- Update changelog. [Adam.Dybbroe]

- Change name of optional (red) band to "redband" [Adam.Dybbroe]

- Fix band naming for OLCI. [Adam.Dybbroe]

v0.6.1 (2018-01-08)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.6.0 → 0.6.1. [Adam.Dybbroe]

- Make it possible to plot multiple bands matching the requested
  wavelength. [Adam.Dybbroe]

- Bugfix check for wavelength range in nir reflectance, and improve unit
  tests. [Adam.Dybbroe]

- Add static data for unit testing. [Adam.Dybbroe]

- Improve unit test coverage. [Adam.Dybbroe]

- Update badges: Refer to develop instead of pre-master. [Adam.Dybbroe]

v0.6.0 (2018-01-05)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.5.2 → 0.6.0. [Adam.Dybbroe]

v0.5.2 (2018-01-05)
-------------------

Fix
~~~

- Bugfix: Move appdirs usage to the config. [Adam.Dybbroe]

Other
~~~~~

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.5.1 → 0.5.2. [Adam.Dybbroe]

- Improve documentation of the NIR emissive part of the 3.x reflectance
  derivations, using more condensed code example. [Adam.Dybbroe]

- Merge pull request #20 from pytroll/appdirs. [Adam Dybbroe]

  Appdirs

- Bugfix, module misspelled. [Adam.Dybbroe]

- Merge branch 'develop' into appdirs. [Adam.Dybbroe]

  Conflicts:
  	pyspectral/utils.py

- Merge pull request #19 from pytroll/radiance_tb_conversions. [Adam
  Dybbroe]

  Radiance tb conversions

- Fix code quality issues from Codacy and Codeclimate. [Adam.Dybbroe]

- Add tests for emissive part of the r37 refl derivations and
  radiance2tb conversions. [Adam.Dybbroe]

- Fix bug for wavenumber conversion in native seviri rsr reader. The bug
  affected the conversion in python 3, and probably not in Py2.
  [Adam.Dybbroe]

- Fix doc tests. [Adam.Dybbroe]

- Fixing doc tests for python 3. [Adam.Dybbroe]

- Merge branch 'radiance_tb_conversions' of
  github.com:pytroll/pyspectral into radiance_tb_conversions.
  [Adam.Dybbroe]

  Conflicts:
  	doc/37_reflectance.rst


- Fix doc tests for py3. [Adam.Dybbroe]

- Utf-8 decode of strings from rsr hdf5 files. Needed for python 3.
  [Adam.Dybbroe]

- Fix for doc tests. [Adam.Dybbroe]

- Rearrange and improve documentation on 3.7 reflectance derivations.
  [Adam.Dybbroe]

- Move up radiance definitions and theory a bit. [Adam.Dybbroe]

- Fix for VIIRS I- and M-bands. Make it possible to make tb<->radiance
  conversions without the LUT. Fix derivation of emissive part.
  [Adam.Dybbroe]

- Fix tb-radiance conversion so it can only be done on the specific band
  in question. [Adam.Dybbroe]

- Rearrange doc pages, moving definitions and theory up a bit. Clean
  away mpop examples. This should be in the PyTroll Gallery instead.
  [Adam.Dybbroe]

- Fix complaints by flake8. [Adam.Dybbroe]

- Allow for derivation of the band integrated radiance, in addition to
  the default, which is the spectral radiance for the band.
  [Adam.Dybbroe]

- Overload the _get_rsr method for the SEVIRI class. RSR data should be
  ignored in the special case of SEVIRI when using off line coefficients
  for the Tb-Radiance conversions. [Adam.Dybbroe]

- Remove method integrate_response. RSR integration is provided by the
  rsr_reader. [Adam.Dybbroe]

- Clean up code, more clear separation of the radiance-tb conversion
  based on RSR and offline derived coefficients for SEVIRI. RSR integral
  is part of the rad-tb conversion class now. Improve unit tests.
  [Adam.Dybbroe]

- Add definition of band integrated radiance. [Adam.Dybbroe]

- Improved function documentation: Specify what the arguments are.
  [Adam.Dybbroe]

- Use appdirs to standardize where pyspectral downloads LUTs and RSR
  files. [Adam.Dybbroe]

- Fix spelling error in doc-pages. [Adam.Dybbroe]

- Add PR and Issue templates - copies from satpy. [Adam.Dybbroe]

v0.5.1 (2017-12-13)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.5.0 → 0.5.1. [Adam.Dybbroe]

- Correct doc strings replacing SLSTR with OLCI. [Adam.Dybbroe]

- Reduce redundant Badge. [Adam.Dybbroe]

- Merge pull request #10 from codacy-badger/codacy-badge. [Adam Dybbroe]

  Add a Codacy badge to README.md

- Add Codacy badge. [The Codacy Badger]

- Corrects the md5sum of the newly updated rsr tar file. [Adam.Dybbroe]

- Bugfix Terra modis response functions. [Adam.Dybbroe]

  Some of the original responses have a few -99 as a response,
  which create wrong central wavelengths in pyspectral

- Instrument names are lower case, variable upper/lower case can be used
  in API. [Adam.Dybbroe]

- Consistent instrument naming, lower case throughout. [Adam.Dybbroe]

- Fix md5sum of latest rsr tar file at zenodo. [Adam.Dybbroe]

v0.5.0 (2017-10-18)
-------------------

Fix
~~~

- Bugfix: default yaml config file had a missing ':' [Adam.Dybbroe]

Other
~~~~~

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.4.3 → 0.5.0. [Adam.Dybbroe]

- Merge pull request #12 from pytroll/yaml_jpss1. [Adam Dybbroe]

  Yaml jpss1
  Tests are passing and coverage has not decreased. Now also RTD builds fine, so ready to merge

- Remove old empty readthedocs req file. [Adam.Dybbroe]

- Revers back to mocking h5py and tqdm when building documentation. Add
  RTD requirements file. [Adam.Dybbroe]

- Don't mock h5py and tqdm. [Adam.Dybbroe]

- Mock trollsift.parser. [Adam.Dybbroe]

- Bugfix, adapt raw readers to new yaml config. [Adam.Dybbroe]

- Mock geotiepoints and not requests for sphinx. [Adam.Dybbroe]

- Add a seperate config.py module. [Adam.Dybbroe]

- Try please RTD concerning yaml. [Adam.Dybbroe]

- Don't mock yaml and six in conf.py. [Adam.Dybbroe]

- Fix automatc versioning in conf.py and mock some more 3rd party sw.
  [Adam.Dybbroe]

- Update documentation of customized config setting. [Adam.Dybbroe]

- Show inheritance in api doc. [Adam.Dybbroe]

- Bring installation documentation up to date. [Adam.Dybbroe]

- Bugfix unit testing the rsr reader. [Adam.Dybbroe]

- Added Himawari-9 and adjusted Himawari-8 AHI RSR files. [Adam.Dybbroe]

- Add rst file with table with supported platforms and sensors.
  [Adam.Dybbroe]

- Add new fromt page header (montage) image. [Adam.Dybbroe]

- Add small tool to compare two pyspectral rsr files. [Adam.Dybbroe]

- Add table showing which sensors are supported. [Adam.Dybbroe]

- Fix original ahi reader to read original excell sheets and add
  Himawari-9. [Adam.Dybbroe]

- Add unittesting for the generic RSR reader. [Adam.Dybbroe]

- Bugfix, download rsr files from zenodo, and improve code style.
  [Adam.Dybbroe]

- Improve code style (following Codacy) [Adam.Dybbroe]

- Update to new RSR tar file including JPSS-1 VIIRS. [Adam.Dybbroe]

- Get the platform_name and sensor from the hdf5 file if not specified
  in the call. [Adam.Dybbroe]

- Store the sensor name in the hdf5 file. [Adam.Dybbroe]

- Add NOAA-20 (JPSS-1) rsr and update Suomi-NPP one with more meta data.
  [Adam.Dybbroe]

- Add pyyaml in the requirements. [Adam.Dybbroe]

- Remove old config file. [Adam.Dybbroe]

- Make it possible to instatiate the RSR class with the rsr filename.
  [Adam.Dybbroe]

- Fix for yaml config. [Adam.Dybbroe]

- Don't show plot when running doctests. [Adam.Dybbroe]

- Add yaml config file, update for JPSS-1 VIIRS and enhance plotting and
  documentation. [Adam.Dybbroe]

v0.4.3 (2017-10-02)
-------------------

Fix
~~~

- Bugfix: Desert aerosol LUT table changed. [Adam.Dybbroe]

Other
~~~~~

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.4.2 → 0.4.3. [Adam.Dybbroe]

- Improve code style: Make codacy more happy. [Adam.Dybbroe]

- More plotting facilities and add documentation on spectral response
  sources. [Adam.Dybbroe]

- Use Rayleigh LUTs from Zenodo. [Adam.Dybbroe]

v0.4.2 (2017-09-15)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.4.1 → 0.4.2. [Adam.Dybbroe]

- Fix doc tests and get rid of duplicate code. [Adam.Dybbroe]

- Update link to internally formatted RSR data. [Adam.Dybbroe]

- Added unit test for atm correction. [Adam.Dybbroe]

- Add simple framework for it atm correction, with old DWD parametric
  method for a start. [Adam.Dybbroe]

- Bugfixing documentation pages. [Adam.Dybbroe]

- Enhance documentation: add simple example how to work with rsr data.
  [Adam.Dybbroe]

- Add debug_on function (copy from satpy) [Adam.Dybbroe]

- RSR data is downloaded from Zenodo. [Adam.Dybbroe]

- Update Dropbox links to LUTs. [Adam.Dybbroe]

- Track the rsr tar file (again) [Adam.Dybbroe]

- Update git-lfs tracked file. [Adam.Dybbroe]

- Fix dropbox link for rsr data file and rayleigh only lut.
  [Adam.Dybbroe]

- Moving the rsr data into the package etc dir. [Adam.Dybbroe]

- Adding rsr-data to git-lfs. [Adam.Dybbroe]

v0.4.1 (2017-07-14)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.4.0 → 0.4.1. [Adam.Dybbroe]

- Deactivate the SEVIRI system tests - these should be in the pytroll
  gallery instead. [Adam.Dybbroe]

- Add rayleight corrected image dor documentation. [Adam.Dybbroe]

- Clean up for easier maintanance. [Adam.Dybbroe]

- Fix requirements: python-geotiepoints >= 1.1.1 is required.
  [Adam.Dybbroe]

- Add Codacy integration. [Adam.Dybbroe]

- Add Scrutinizer integration. [Adam.Dybbroe]

- Correct code version in documentation. [Adam.Dybbroe]

- Add integration with codeclimate. [Adam.Dybbroe]

v0.4.0 (2017-05-19)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.3.4 → 0.4.0. [Adam.Dybbroe]

- Merge branch 'develop' of github.com:pytroll/pyspectral into develop.
  [Adam.Dybbroe]

- Merge pull request #9 from pytroll/autofix/wrapped2_to3_fix. [Adam
  Dybbroe]

  Fix "Prefer `format()` over string interpolation operator" issue

- Migrated `%` string formating. [Cody]

- Merge branch 'feature-new-rayleigh' into develop. [Adam.Dybbroe]

- Fix doctest. [Adam.Dybbroe]

- Fall back to scipy if Cython is not available. [Adam.Dybbroe]

- Fix nearest wavelength search. [Martin Raspaud]

- Clip angles using bounds given in hdf5 file instead of hardcoded
  values. [Adam.Dybbroe]

- Try without using with_system_site_packages for Travis. [Adam.Dybbroe]

- Update requirements file. [Adam.Dybbroe]

- Try solve for slow scipy building on travis. [Adam.Dybbroe]

- Clip satellite-zenith angles outside range. [Adam.Dybbroe]

- Update url's for all aerosol-types. [Adam.Dybbroe]

- Add all aerosol-simulations. [Adam.Dybbroe]

- Don't install standard system-site scipy. [Adam.Dybbroe]

- Fix azimuth angle bug. And prepare for several aerosol types.
  [Adam.Dybbroe]

- Interpolate Rayleigh lut in 3d with fixed wavelength. [Martin Raspaud]

- Try fix scipy installation on travis for py2.7. [Adam.Dybbroe]

- Work on non-masked arrays in rayleigh correction and fix for low sun
  elevation. [Adam.Dybbroe]

- Interpolate rayleigh lut on data points directly. [Martin Raspaud]

- Require scipy 0.14. [Adam.Dybbroe]

- Minimize memory footprint in rayleigh correction. [Adam.Dybbroe]

  However, still requiring too much memory!

- New rayleigh correction - Using 4d interpolation of RTM tables.
  [Adam.Dybbroe]

- Fix typo in doc string. [Adam.Dybbroe]

- Simplify out of bounds check. [Adam.Dybbroe]

- Use format() for string formating and simplify code improving
  readability. [Adam.Dybbroe]

- Bugfix in string formatting. [Adam.Dybbroe]

- Use format() instead of string interpolation operator. [Adam.Dybbroe]

- Class documented. [Adam.Dybbroe]

- Improve string formating. [Adam.Dybbroe]

- Improve doc-strings and syntax. [Adam.Dybbroe]

- Add quantifiedcode badge. [Adam.Dybbroe]

v0.3.4 (2017-04-03)
-------------------

Fix
~~~

- Bugfix: unttests and py2.7. [Adam.Dybbroe]

Other
~~~~~

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.3.3 → 0.3.4. [Adam.Dybbroe]

- Merge branch 'pre-master' into release-v0.3.4. [Adam.Dybbroe]

- Pep8 and increasing pylint score. [Adam.Dybbroe]

- Add test module. [Adam.Dybbroe]

- Add unitest for aatsr reader. [Adam.Dybbroe]

- Remove python 3.3 from travis: does not build scipy. [Adam.Dybbroe]

- Pep8 and improving pylint scores. [Adam.Dybbroe]

- Add TRAVIS tests on various Python 3 versions. [Adam.Dybbroe]

- Travis fix: Remove system-site-packages on anything else than 2.7.
  [Adam.Dybbroe]

- Don't set python version for travis. [Adam.Dybbroe]

- Activate python3 testing to travis. [Adam.Dybbroe]

- Make Python 3 compatible. [Adam.Dybbroe]

- Epsilon is a input parameter not a hardcoded value anymore.
  [Adam.Dybbroe]

- Improved sun-sat viewing figure for docs. [Adam.Dybbroe]

- Fix unittests near-ir reflectance. [Adam.Dybbroe]

- LUT file can be generated even without having the filename defined in
  config. [Adam.Dybbroe]

  Also, only NIR bands in the 3.5-3.95 range is supported

- Remove duplicate code and move get_bandname_from_wavelength to utils.
  [Adam.Dybbroe]

- Fixed the 180 degree azimuth bug in the Rayleigh correction, and
  improved documentation. [Adam.Dybbroe]

- Merge pull request #5 from pytroll/rayleigh-speedup. [Adam Dybbroe]

  Speedup and optimize rayleigh computations

- Remove unneeded variable. [Martin Raspaud]

- Speedup and optimize rayleigh computations. [Martin Raspaud]

- Remove old code commentedt out. [Adam.Dybbroe]

- Correctied emissive part: Allow reflectances outside [0,1] and apply
  correction. [Adam.Dybbroe]

- More strict masking: Avoid crazy r39 values due to very small or
  negative denominators. [Adam.Dybbroe]

- Merge branch 'release-v0.3.3' into pre-master. [Adam.Dybbroe]

- Merge branch 'release-v0.3.3' [Adam.Dybbroe]

v0.3.3 (2017-01-13)
-------------------

Fix
~~~

- Bugfix: include pyspectral/etc instead of etc. [Adam.Dybbroe]

Other
~~~~~

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.3.2 → 0.3.3. [Adam.Dybbroe]

- Merge branch 'pre-master' into release-v0.3.3. [Adam.Dybbroe]

- Merge branch 'release-v0.3.2' into pre-master. [Adam.Dybbroe]

- Merge branch 'release-v0.3.2' [Adam.Dybbroe]

v0.3.2 (2017-01-13)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.3.1 → 0.3.2. [Adam.Dybbroe]

- Merge branch 'pre-master' into release-v0.3.2. [Adam.Dybbroe]

- Bugfix, getting the filename of the config file right with
  pkg_resources. [Adam.Dybbroe]

- Fix problem finding the config file in certain environments.
  [Adam.Dybbroe]

  Include pyspectral.cfg in the package_data instead of the data_files.
  Move pyspctral.cfg down to the pyspectral package dir and use pkg_resources

- Bugfix. Allow rayleigh reflectances (set to zero) outide the 400-800
  nm range. [Adam.Dybbroe]

- Merge branch 'release-v0.3.1' into pre-master. [Adam.Dybbroe]

- Merge branch 'release-v0.3.1' [Adam.Dybbroe]

v0.3.1 (2016-11-28)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.3.0 → 0.3.1. [Adam.Dybbroe]

- Merge branch 'pre-master' into release-v0.3.1. [Adam.Dybbroe]

- Add simple plot script. [Adam.Dybbroe]

- Add raw GOES-R abi rsr-reader and simple plot script. [Adam.Dybbroe]

- Merge branch 'pre-master' into release-v0.3.1. [Adam.Dybbroe]

- Add description of Rayleigh correction capability. [Adam.Dybbroe]

- Update documentation with the built-in default configuration.
  [Adam.Dybbroe]

- Fix default configuration using expanduser. [Adam.Dybbroe]

- Add pandas to extra requirement. [Adam.Dybbroe]

- Add more instruments to the default cfg file. Remove deprecated
  template file. [Adam.Dybbroe]

- Merge branch 'release-v0.3.0' into pre-master. [Adam.Dybbroe]

- Merge branch 'release-v0.3.0' [Adam.Dybbroe]

v0.3.0 (2016-11-21)
-------------------

- Update changelog. [Adam.Dybbroe]

- Bump version: 0.2.7 → 0.3.0. [Adam.Dybbroe]

- Merge branch 'pre-master' into release-v0.3.0. [Adam.Dybbroe]

- Makes it possible to do rayleigh correction without access to the
  spectral responses. [Adam.Dybbroe]

- Add back all unittests for rayleigh correction. [Adam.Dybbroe]

- Travis needs the package libhdf5-serial-dev. [Adam.Dybbroe]

- H5py is required. [Adam.Dybbroe]

- Try getting Travis to be happy. [Adam.Dybbroe]

- Remove some imports from test-code. [Adam.Dybbroe]

- Add more unittesting of the rayleigh correction code. [Adam.Dybbroe]

- Take away rayleigh unittests for the moment. [Adam.Dybbroe]

- Add unit tests for rayleigh correction utilities. [Adam.Dybbroe]

- Added original MSG rsr data file. [Adam.Dybbroe]

- Add requirements file - Travis seems to need it. [Adam.Dybbroe]

- Make pyling happier. [Martin Raspaud]

- Fix typo in constant name (rural aerosols url) [Martin Raspaud]

- Bugfix get_bandname_from_wavelength. [Martin Raspaud]

- Reorganize imports in rayleigh.py. [Martin Raspaud]

- Allow nominal wavelength as input. [Adam.Dybbroe]

- Fix doc tests. [Adam.Dybbroe]

- Download rsr files automagically. [Adam.Dybbroe]

- License is GPLv3. [Adam.Dybbroe]

- Merge branch 'rayleigh' into pre-master. [Adam.Dybbroe]

  Conflicts:
  	pyspectral/avhrr_rsr.py
  	pyspectral/utils.py
  	setup.py


- Don't go further than 88 deg sunz when doin rayleigh corr.
  [Adam.Dybbroe]

- Clip rayleigh correction to keep it between 0 and 100. [Adam.Dybbroe]

- Use expanduser to the get the full path correctly. [Adam.Dybbroe]

- One function to get configuration. [Adam.Dybbroe]

- Bugfix. [Adam.Dybbroe]

- Introduce default config file. [Adam.Dybbroe]

- Rayleigh correction depends on reflectance + Download LUTS
  automagically. [Adam.Dybbroe]

- Remove requirements file. Requirements are specified in setup.py.
  [Adam.Dybbroe]

- Remove scipy from req-file. [Adam.Dybbroe]

  RTD doesn't like it!

- Testing putting back scipy in req-file. [Adam.Dybbroe]

- Move req file for RTD. [Adam.Dybbroe]

- Remove scipy from requirement file... [Adam.Dybbroe]

  scipy cannot be in requirements.txt if RTD should work

- Consistent requirements on scipy version. [Adam.Dybbroe]

- Put back scipy in requirements file and make a RTD req file.
  [Adam.Dybbroe]

- Putting back scipy requirement. [Adam.Dybbroe]

- Remove scipy from requirements file. [Adam.Dybbroe]

- Remove scipy as a requirement in setup file to see of readthecos like
  it better. [Adam.Dybbroe]

- Try fixing mockup in docs, so readthedocs is satisfied. [Adam.Dybbroe]

- Try mockup more scipy stuff to let readthedocs compile. [Adam.Dybbroe]

- Activate option to use various atmospheres. [Adam.Dybbroe]

- Try fix readthedocs problems. [Adam.Dybbroe]

- Add Rayleigh correction functionality. [Adam.Dybbroe]

v0.2.7 (2016-11-01)
-------------------

Fix
~~~

- Bugfix: radiance mask was not initialised. [Adam.Dybbroe]

- Bugfix: lut table is now read once it has been written. [Adam.Dybbroe]

Other
~~~~~

- Update changelog. [Martin Raspaud]

- Bump version: 0.2.6 → 0.2.7. [Martin Raspaud]

- Merge branch 'pre-master' into release-v0.2.7. [Martin Raspaud]

- Add Sentinel-3 OLCI. [Adam.Dybbroe]

- Add bump and changelog config files. [Martin Raspaud]

- Merge branch 'pre-master' [Adam.Dybbroe]

- Add more satellites to the config-template and bump version number.
  [Adam.Dybbroe]

- Merge branch 'master' into pre-master. [Adam.Dybbroe]

- Bump version number. [Adam.Dybbroe]

- Merge branch 'pre-master' [Adam.Dybbroe]

- Merge branch 'pre-master' [Adam.Dybbroe]

- Add support for NOAA-15 rsr data. [Adam.Dybbroe]

- Fix md5sum of new tar file in dropbox. [Adam.Dybbroe]

- Add avhrr/1. [Adam.Dybbroe]

- Update documentation to reflect the further sensors included.
  [Adam.Dybbroe]

- Add simple example plotting routine. [Adam.Dybbroe]

- Add support for slstr, and add more avhrr sensors. [Adam.Dybbroe]

- Add support for AATSR. [Adam.Dybbroe]

- Improvements in documentation as suggested by Ulrich May 2016.
  [Adam.Dybbroe]

- Merge branch 'master' into pre-master. [Adam.Dybbroe]

  Conflicts:
  	README.md

- Remove python 3.2 as it fails in travis due to scipy. [Adam.Dybbroe]

- Try fix errors on Travis, and go back to py 3.3 from 3.2.
  [Adam.Dybbroe]

- System site packages false to try let py 3.3 go through on travis.
  [Adam.Dybbroe]

- Test travis on python 3.3, and try fix the automatic deployment from
  travis. [Adam.Dybbroe]

- Changed pypi password. [Adam.Dybbroe]

- Fix version in setup and travis password encryption. [Adam.Dybbroe]

- Fix version number. [Adam.Dybbroe]

- Fix coverage status badge. [Adam.Dybbroe]

- Fix for travis. [Adam.Dybbroe]

- Fixes for travis, deploy on all branches if a tag is set.
  [Adam.Dybbroe]

- Fix travis and landscape badges - use pre-master for status indicator.
  [Adam.Dybbroe]

- Fix repo name for travis and pypi deployment. [Adam.Dybbroe]

- Merge branch 'pre-master' [Adam.Dybbroe]

- Merge branch 'pre-master' [Adam.Dybbroe]

- Merge branch 'pre-master' [Adam Dybbroe]

- Merge branch 'pre-master' [Adam Dybbroe]

- Merge branch 'pre-master' [Adam Dybbroe]

- Merge branch 'master' of github.com:adybbroe/pyspectral. [Adam
  Dybbroe]

  Conflicts:
  	README.md


- Removed broken Version tag/badge. [Adam.Dybbroe]

- Extend get_central_wave function to allow a weight different from 1
  (default) [Adam.Dybbroe]

  For instance a weight = 1./lambda**4 can be added in order to get the
  effective wavelength relevant when doing Rayleigh scattering calculations

- Fix badge for pypi version. [Adam.Dybbroe]

- Merge branch 'develop' into pre-master. [Adam.Dybbroe]

- Add Depsy badge. [Adam.Dybbroe]

- Fix inconsistency between using LUT or not. [Adam.Dybbroe]

- Handle instrument name avhrr/3 (mpop style instrument naming)
  [Adam.Dybbroe]

- Add for instrument viirs in r37 derivation. [Adam.Dybbroe]

- Implements wavelength to wavenumber conversion for rsr integration.
  [Adam.Dybbroe]

  Code works, but needs to be checked if the conversion is correct

- Introduce radiance to temperature conversion capability.
  [Adam.Dybbroe]

- Add derivation of the emissive part of the 3.x signal. [Adam.Dybbroe]

- Add radiance to temperature conversion for wave numbers.
  [Adam.Dybbroe]

  Inverse Planck function added for wave number space

- Bugfix viirs rsr. [Adam.Dybbroe]

- Adding back the inband_solarirradiance function. [Adam.Dybbroe]

- Merge branch 'develop' into pre-master. [Adam.Dybbroe]

- Bugfix. [Adam.Dybbroe]

- Bugfixing a couple of interfaces. [Adam.Dybbroe]

- Merge branch 'himawari' into develop. [Adam.Dybbroe]

  Conflicts:
  	etc/pyspectral.cfg_template
  	pyspectral/modis_rsr.py
  	pyspectral/near_infrared_reflectance.py
  	pyspectral/tests/test_reflectance.py
  	pyspectral/tests/test_solarflux.py

- Change in the raw terra reader to read the inb.final files instead.
  [Adam.Dybbroe@smhi.se]

- Fix unit tests to be more tolerant for numerical precision. [Adam
  Dybbroe]

- Fix out of index bounds problem in LUT table. [Adam Dybbroe]

- Test program using 2d arrays. [Adam Dybbroe]

- Bug fix, and logging. [Adam Dybbroe]

- 3.8 reflectance with the AHI channel 7. [Adam Dybbroe]

- Add template config file also with the AHI stuff. [Adam Dybbroe]

- Adding rsr reader for Himawari AHI (data from from CIMSS) [Adam
  Dybbroe]

- Bugfix. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam.Dybbroe]

- Merge branch 'develop' into pre-master. [Adam.Dybbroe]

- Fixing template config file. [Adam.Dybbroe]

- Merge branch 'develop' into pre-master. [Adam.Dybbroe]

- Fixing small bugs and the doc tests. [Adam.Dybbroe]

- Merge branch 'platform_name' into develop. [Adam.Dybbroe]

- Use direct path to RSR data if given in config, otherwise join
  rsr_dir, platform_name and instrument. [Panu Lahtinen]

- Update config for WMO/OSCAR naming and similarly named RSR files.
  [Panu Lahtinen]

- AVHRR instrument name is one of "avhrr", "avhrr3" or "avhrr/3" [Panu
  Lahtinen]

- Fixed incorrect variable names, PEP8 work. [Panu Lahtinen]

- Replaced satname and satnum with platform_name, added AVHRR, use only
  WMO OSCAR naming, added gitignore, PEP8 work, version number bumbed
  up. [Panu Lahtinen]

- Add config for bdist_rpm. [Martin Raspaud]

- Fixed unit test. [Adam.Dybbroe@smhi.se]

- Update raw modis reader for Terra - use 'rsr.<BANDNUMBER>.inb.final'
  [Adam.Dybbroe@smhi.se]

- Allow for negative 3.9 reflectances. [Adam Dybbroe]

- Minimise masking: Allow for negative 3.9 reflectances. [Adam Dybbroe]

- Meteosat satellite numbers should be with two letters! [Adam Dybbroe]

- More log info in case no rsr file is found matching sat and number.
  [Adam Dybbroe]

- Fixed mail address in header. [Adam Dybbroe]

- Cosmetics. [Adam Dybbroe]

- File header corrected. [Adam Dybbroe]

- Fixing author mail adresses in headers. [Adam Dybbroe]

- Fixing author mail adresses in headers. [Adam Dybbroe]

- Editorial. [Adam Dybbroe]

- Fixed copyright year. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

- Adding rgb imagery to the doc pages. [Adam Dybbroe]

- Merge branch 'smhi' of /data/proj/SAF/GIT/pyspectral into develop.
  [Adam Dybbroe]

  Conflicts:
  	MANIFEST.in


- Added pyspectral.cfg.template file path to manifest file. [Adam
  Dybbroe]

- Adding config file for smhi. [Adam Dybbroe]

- Adding manifest file. [Adam Dybbroe]

- Adding setup.cfg to smhi branch. [Adam Dybbroe]

- Added paths to MANIFEST file. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

- Adding tests for rad<->tb conversion. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

- Removing memory profiling. [Adam Dybbroe]

- Moving global parameter BANDNAMES to utils. [Adam Dybbroe]

- Bugfix. [Adam Dybbroe]

- Don't require config file to be present for near-ir derivations. [Adam
  Dybbroe]

- Fixing support for writing/reading radiance to tb lut's. [Adam
  Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

- Fixing code status banners on github pages. [Adam Dybbroe]

- Code health status added to develop branch on github. [Adam Dybbroe]

- Fixing bug in documentation - planck function. [Adam Dybbroe]

- Documenting how to download the rsr data. [Adam Dybbroe]

- Fixing spell error in internal h5 files. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

- Merge branch 'rsr_restructure' into develop. [Adam Dybbroe]

- Bug fixes and corrections to the reflectance calculations. Added units
  and scale. [Adam Dybbroe]

- Extending docs. [Adam Dybbroe]

- Adding tests for radiance <-> tb conversions. Fixing bug in tb to
  radiance conversion. [Adam Dybbroe]

- Improving unittest and docs. [Adam Dybbroe]

- Fixing bug in and testing blackbody_wn. [Adam Dybbroe]

- Capitalized the constant names and removed a douplicate import. [ropf]

- Autopep8. [Adam Dybbroe]

- Pep8 from autopep8. [Adam Dybbroe]

- Pep8. [Adam Dybbroe]

- Fixing documentation -> pass doc tests. [Adam Dybbroe]

- Testing pre-commit hooks. [Adam Dybbroe]

- Added test_util.py. [Adam Dybbroe]

- Provoke an error in the tests. [Adam Dybbroe]

- ...again. [Adam Dybbroe]

- Test triggering pre-commit hook. [Adam Dybbroe]

- Test trigger pre-commit hooks. [Adam Dybbroe]

- Remove empty line. [Adam Dybbroe]

- Rearranged tests and added a switch for Travis. [Adam Dybbroe]

- Bugfix for Travis. [Adam Dybbroe]

- Fixing for units and wavelength<->wavenumber conversions. [Adam
  Dybbroe]

- Fixing trivial things in documentation. [Adam Dybbroe]

- Mocking a unittest. Commenting out the doc tests. [Adam Dybbroe]

- Change name of class from Calculator to RadTbConverter. [Adam Dybbroe]

- Fixing the unittests. [Adam Dybbroe]

- Fixing docs and removing old redundant code. [Adam Dybbroe]

- Restructuring continued: Readin rsr data from one unified hdf5 format.
  [Adam Dybbroe]

- Added customization support for Landscape. [Adam Dybbroe]

- Adjust instrument readers. [Adam Dybbroe]

- Adjusted unittests. [Adam Dybbroe]

- Further enhancements towards unified reading. [Adam Dybbroe]

- Writng AVHRR and SEVIRI rsr to internal hdf5 format. [Adam Dybbroe]

- Prepare for a restructure of the reflectance and tb2radiance parts.
  [Adam Dybbroe]

- Correcting the Planck constant. [Adam Dybbroe]

- Fixed for VIIRS. [Adam Dybbroe]

- Adding support for N19 AVHRR. [Adam Dybbroe]

- Bugfix. [Adam Dybbroe]

- Adding for pypi deployment. [Adam Dybbroe]

- Choose develop branch for the coverage/build results on github. [Adam
  Dybbroe]

- Added for coveralls and build status (travis ci) on github. [Adam
  Dybbroe]

- Support for coveralls. [Adam Dybbroe]

- Fixing the test suite... [Adam Dybbroe]

- Making a test suite, as e.g. discussed at
  http://mindref.blogspot.de/2010/06/python-setuptools.html. [Adam
  Dybbroe]

- Cleaning up in tests. [Adam Dybbroe]

- No doc tests for the time being... [Adam Dybbroe]

- Bug in setup script fixed. [Adam Dybbroe]

- Travis CI. [Adam Dybbroe]

- Travis CI adaptations. [Adam Dybbroe]

- Travis CI stuff to try get numpy and scipy available. [Adam Dybbroe]

- Travis CI: Trying to fix scipy installation problems. [Adam Dybbroe]

- Changing travis setups. [Adam Dybbroe]

- Adding support for travis ci. [Adam Dybbroe]

- Added the api.rst file. [Adam Dybbroe]

- Added API documentation. [Adam Dybbroe]

- Adding CO2 correction of the 3.9 micron radiance. [Adam Dybbroe]

- Passing tests. [Adam Dybbroe]

- Typo in docs fixed. [Adam Dybbroe]

- Allowing for calcualtions in wavenumbers as well. Better
  documentation. Modified Seviri reader. [Adam Dybbroe]

- Added VIIRS reader. Added blackbody radiation calculations using wave
  numbers Improved relfectance code. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

- Reading/loading data automatically and handles dynamic loading of
  configuration. [Adam Dybbroe]

- Added doc testing. [Martin Raspaud]

- Doc fixes. [Adam Dybbroe]

- Fixing bug in docs. [Adam Dybbroe]

- Improve the error handling in case of wrong environment. [Adam
  Dybbroe]

- Adding LUT option and changing reflectance module to allow reflectance
  derivation of entire imager scenes. [Adam Dybbroe]

- Fixing bug in docs. [Adam Dybbroe]

- Documenting the 3.7 reflectance derivation. [Adam Dybbroe]

- Adding new rst files. [Adam Dybbroe]

- Improving documentation. [Adam Dybbroe]

- Added SEVIRI example to the docs. [Adam Dybbroe]

- Adding seviri reader and some more documentation. [Adam Dybbroe]

- Fixing for MODIS terra as well. [Adam Dybbroe]

- Add one more use case to doc. [Adam Dybbroe]

- Merge branch 'pre-master' into develop. [Adam Dybbroe]

- Merge branch 'develop' into pre-master. [Adam Dybbroe]

  Conflicts:
  	tests/test_solarflux.py


- Merge branch 'master' of github.com:adybbroe/pyspectral into pre-
  master. [Adam Dybbroe]

  Conflicts:
  	README.md


- Initial commit. [Adam Dybbroe]

- Add logging and documentation. [Adam Dybbroe]

- Adding support for the calculation of the 3.7 solar relfectance. [Adam
  Dybbroe]

- First unittests added. [Adam Dybbroe]

- First time in git... [Adam Dybbroe]


