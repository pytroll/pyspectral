Changelog
=========

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


