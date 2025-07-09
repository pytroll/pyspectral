## Version 0.13.6 (2025/07/09)

### Issues Closed

* [Issue 244](https://github.com/pytroll/pyspectral/issues/244) - Seeking References for “near_infrared_reflectance”
* [Issue 238](https://github.com/pytroll/pyspectral/issues/238) - Eliminate division warning of blackbody_wn_rad2temp

In this release 2 issues were closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 254](https://github.com/pytroll/pyspectral/pull/254) - Fix broken link to MSG interpretation guide
* [PR 235](https://github.com/pytroll/pyspectral/pull/235) - Remove deprecated aerosol_type download_luts usage in rayleigh

#### Features added

* [PR 246](https://github.com/pytroll/pyspectral/pull/246) - Tiny fix simplifying the rsr plot code
* [PR 240](https://github.com/pytroll/pyspectral/pull/240) - Fix rsr plotting to allow for similar (overlapping) bands

#### Documentation changes

* [PR 254](https://github.com/pytroll/pyspectral/pull/254) - Fix broken link to MSG interpretation guide

In this release 5 pull requests were closed.


## Version 0.13.5 (2024/09/24)

### Pull Requests Merged

#### Features added

* [PR 234](https://github.com/pytroll/pyspectral/pull/234) - Add support for Sentinel-2C

In this release 1 pull request was closed.


## Version v0.13.4 (2024/08/14)

### Issues Closed

* [Issue 229](https://github.com/pytroll/pyspectral/issues/229) - Deprecate old scipy and remove use of trapz (numpy and scipy) ([PR 233](https://github.com/pytroll/pyspectral/pull/233) by [@djhoese](https://github.com/djhoese))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 233](https://github.com/pytroll/pyspectral/pull/233) - Replace deprecated numpy trapezoid/trapz usage with scipy trapezoid ([229](https://github.com/pytroll/pyspectral/issues/229))
* [PR 232](https://github.com/pytroll/pyspectral/pull/232) - Cleanup unused dependencies and deprecated code

In this release 2 pull requests were closed.


## Version v0.13.3 (2024/07/17)

### Pull Requests Merged

#### Bugs fixed

* [PR 231](https://github.com/pytroll/pyspectral/pull/231) - Updated the file name for the FY-3F Mersi-3 RSRs

#### Features added

* [PR 226](https://github.com/pytroll/pyspectral/pull/226) - Add RSR script for MERSI-3 onboard FY-3F

In this release 2 pull requests were closed.


## Version v0.13.2 (2024/06/27)

### Issues Closed

* [Issue 227](https://github.com/pytroll/pyspectral/issues/227) - Pyspectral 0.13.1 not compatible with SciPy 1.14.x -> update dependencies ([PR 228](https://github.com/pytroll/pyspectral/pull/228) by [@djhoese](https://github.com/djhoese))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 228](https://github.com/pytroll/pyspectral/pull/228) - Fix scipy 1.14 compatibility and trapz usage ([227](https://github.com/pytroll/pyspectral/issues/227))

In this release 1 pull request was closed.


## Version v0.13.1 (2024/05/07)

### Issues Closed

* [Issue 219](https://github.com/pytroll/pyspectral/issues/219) - [Question] Using red-band for the representation
* [Issue 193](https://github.com/pytroll/pyspectral/issues/193) - Question: Is there any details about LUT?

In this release 2 issues were closed.

### Pull Requests Merged

#### Features added

* [PR 225](https://github.com/pytroll/pyspectral/pull/225) - Add fengyun and geo-kompsat-2b sensor support
* [PR 224](https://github.com/pytroll/pyspectral/pull/224) - Add support and RSR converter for the GOCI2 instrument aboard GK-2B
* [PR 223](https://github.com/pytroll/pyspectral/pull/223) - Add RSR convert script for MERSI-1 on FY-3A/B/C
* [PR 222](https://github.com/pytroll/pyspectral/pull/222) - Add a RSR convert script for FY-3G MERSI-RM sensor
* [PR 192](https://github.com/pytroll/pyspectral/pull/192) - Add a RSR convert script for FY-4B GHI sensor

In this release 5 pull requests were closed.


## Version v0.13.0 (2023/11/27)

### Issues Closed

* [Issue 205](https://github.com/pytroll/pyspectral/issues/205) - Near infrared reflectance calculation does not preserve input dtype ([PR 206](https://github.com/pytroll/pyspectral/pull/206) by [@pnuu](https://github.com/pnuu))
* [Issue 201](https://github.com/pytroll/pyspectral/issues/201) - blackbody functions not dask friendly, trigger early dask computation

In this release 2 issues were closed.

### Pull Requests Merged

#### Features added

* [PR 208](https://github.com/pytroll/pyspectral/pull/208) - Update the solar spectrum code to use the included reference spectra
* [PR 207](https://github.com/pytroll/pyspectral/pull/207) - Remove pkg_resources usage in config handling
* [PR 206](https://github.com/pytroll/pyspectral/pull/206) - Return 3.x um reflectance with the same dtype as the NIR data ([205](https://github.com/pytroll/pyspectral/issues/205))
* [PR 204](https://github.com/pytroll/pyspectral/pull/204) - Bump up python versions
* [PR 203](https://github.com/pytroll/pyspectral/pull/203) - Allow dataarrays and preserve dtype in rad2temp
* [PR 202](https://github.com/pytroll/pyspectral/pull/202) - Update the solar spectrum code to use the included reference spectra

In this release 6 pull requests were closed.


## Version 0.12.5 (2023/09/21)

### Pull Requests Merged

#### Bugs fixed

* [PR 195](https://github.com/pytroll/pyspectral/pull/195) - Fix rayleigh not preserving input dtype

In this release 1 pull request was closed.


## Version v0.12.4 (2023/09/20)

### Issues Closed

* [Issue 177](https://github.com/pytroll/pyspectral/issues/177) - Unit Convert Error in the Doc. ([PR 180](https://github.com/pytroll/pyspectral/pull/180) by [@adybbroe](https://github.com/adybbroe))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 197](https://github.com/pytroll/pyspectral/pull/197) - Overhaul build process with setuptools_scm and written version file
* [PR 180](https://github.com/pytroll/pyspectral/pull/180) - Bugfix in function doc header ([177](https://github.com/pytroll/pyspectral/issues/177))

#### Documentation changes

* [PR 180](https://github.com/pytroll/pyspectral/pull/180) - Bugfix in function doc header ([177](https://github.com/pytroll/pyspectral/issues/177))

In this release 3 pull requests were closed.


## Version v0.12.3 (2022/11/22)

### Issues Closed

* [Issue 172](https://github.com/pytroll/pyspectral/issues/172) - Bug plotting spectral responses with MODIS ([PR 174](https://github.com/pytroll/pyspectral/pull/174) by [@adybbroe](https://github.com/adybbroe))
* [Issue 166](https://github.com/pytroll/pyspectral/issues/166) - raise keyerror when loading B07 of himawari_ahi using DataQuery
* [Issue 155](https://github.com/pytroll/pyspectral/issues/155) - NOAA-6 spectral responses are wrong for channel 1 & 2
* [Issue 149](https://github.com/pytroll/pyspectral/issues/149) - Add FY4B AGRI bands
* [Issue 143](https://github.com/pytroll/pyspectral/issues/143) - Implement RSRs for AGRI aboard FengYun-4B ([PR 171](https://github.com/pytroll/pyspectral/pull/171) by [@simonrp84](https://github.com/simonrp84))

In this release 5 issues were closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 174](https://github.com/pytroll/pyspectral/pull/174) - Fix bug getting bandname from RSR data ([172](https://github.com/pytroll/pyspectral/issues/172))

#### Features added

* [PR 173](https://github.com/pytroll/pyspectral/pull/173) - Fix4agri on fy4a and fy4b
* [PR 171](https://github.com/pytroll/pyspectral/pull/171) - Update for FY-4B ([143](https://github.com/pytroll/pyspectral/issues/143))

In this release 3 pull requests were closed.


## Version 0.12.2 (2022/10/24)

### Issues Closed

* [Issue 164](https://github.com/pytroll/pyspectral/issues/164) - Pyspectral is trying to read wrong RSR file for FY-3D/MERSI-2 ([PR 165](https://github.com/pytroll/pyspectral/pull/165) by [@adybbroe](https://github.com/adybbroe))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 165](https://github.com/pytroll/pyspectral/pull/165) - Bugfix Mersi-2 RSR filename ([164](https://github.com/pytroll/pyspectral/issues/164))

In this release 1 pull request was closed.


## Version v0.12.1 (2022/10/20)


### Pull Requests Merged

#### Bugs fixed

* [PR 162](https://github.com/pytroll/pyspectral/pull/162) - Fix: check_and_download() got an unexpected keyword argument 'aerosol_type'

#### Features added

* [PR 163](https://github.com/pytroll/pyspectral/pull/163) - Remove author names from headers and tidy up for flake8 issues

In this release 2 pull requests were closed.


## Version v0.12.0 (2022/10/11)

### Issues Closed

* [Issue 127](https://github.com/pytroll/pyspectral/issues/127) - AVHRR instrument naming - allow avhrr-# ([PR 136](https://github.com/pytroll/pyspectral/pull/136) by [@adybbroe](https://github.com/adybbroe))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 159](https://github.com/pytroll/pyspectral/pull/159) - Revert np.nan_to_num usage on rayleigh correction array
* [PR 158](https://github.com/pytroll/pyspectral/pull/158) - Fix RSR band name retrieval for unconfigured sensors
* [PR 157](https://github.com/pytroll/pyspectral/pull/157) - Fix noaa6 rsr
* [PR 153](https://github.com/pytroll/pyspectral/pull/153) - Fix a minor formatting bug in the atm-correction RTD pages
* [PR 136](https://github.com/pytroll/pyspectral/pull/136) - Fix avhrr instrument naming ([127](https://github.com/pytroll/pyspectral/issues/127))

#### Features added

* [PR 156](https://github.com/pytroll/pyspectral/pull/156) - Add support for NOAA-21 VIIRS
* [PR 152](https://github.com/pytroll/pyspectral/pull/152) - EPS-SG VII (METimage) channel names added
* [PR 150](https://github.com/pytroll/pyspectral/pull/150) - Add AGRI bands to the BANDNAMES dict
* [PR 148](https://github.com/pytroll/pyspectral/pull/148) - Updated the FCI spectral responses as of April 2022
* [PR 145](https://github.com/pytroll/pyspectral/pull/145) - Add converter for Arctica-M N1 RSR data.
* [PR 136](https://github.com/pytroll/pyspectral/pull/136) - Fix avhrr instrument naming ([127](https://github.com/pytroll/pyspectral/issues/127))

#### Documentation changes

* [PR 154](https://github.com/pytroll/pyspectral/pull/154) - Cleanup RSR and LUT download functions for clearer usage
* [PR 153](https://github.com/pytroll/pyspectral/pull/153) - Fix a minor formatting bug in the atm-correction RTD pages

In this release 13 pull requests were closed.


## Version v0.11.0 (2022/03/01)


### Pull Requests Merged

#### Features added

* [PR 144](https://github.com/pytroll/pyspectral/pull/144) - Add converter for Electro-L N2 MSU/GS spectral response functions
* [PR 133](https://github.com/pytroll/pyspectral/pull/133) - Refactor rayleigh correction to be more dask friendly

In this release 2 pull requests were closed.


## Version v0.10.6 (2021/12/22)

### Issues Closed

* [Issue 137](https://github.com/pytroll/pyspectral/issues/137) - Bug in rayleigh correction related to Dask version >= 2021.5.1 ([PR 138](https://github.com/pytroll/pyspectral/pull/138) by [@adybbroe](https://github.com/adybbroe))
* [Issue 132](https://github.com/pytroll/pyspectral/issues/132) - Add GOES-18 and GOES-19 RSRs ([PR 142](https://github.com/pytroll/pyspectral/pull/142) by [@adybbroe](https://github.com/adybbroe))

In this release 2 issues were closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 138](https://github.com/pytroll/pyspectral/pull/138) - Bugfix unittests rayleigh ([137](https://github.com/pytroll/pyspectral/issues/137))

#### Features added

* [PR 142](https://github.com/pytroll/pyspectral/pull/142) - Creating ABI RSR files for GOES 18 & 19 (FM3 & 4) ([132](https://github.com/pytroll/pyspectral/issues/132))
* [PR 141](https://github.com/pytroll/pyspectral/pull/141) - Add technique to reduce Rayleigh contribution at high zenith angles
* [PR 140](https://github.com/pytroll/pyspectral/pull/140) - Fix for deprecation warnings concerning clipping in Rayleigh part
* [PR 135](https://github.com/pytroll/pyspectral/pull/135) - Remove all use of 'six'
* [PR 134](https://github.com/pytroll/pyspectral/pull/134) - Change tested Python versions to 3.8, 3.9 and 3.10

In this release 6 pull requests were closed.


## Version v0.10.5 (2021/04/29)

### Pull Requests Merged

#### Bugs fixed

* [PR 129](https://github.com/pytroll/pyspectral/pull/129) - Fix so reflectances can be derived from scalar inputs

#### Features added

* [PR 128](https://github.com/pytroll/pyspectral/pull/128) - Fix dask compatibility of IR atmospherical correction

#### Documentation changes

* [PR 129](https://github.com/pytroll/pyspectral/pull/129) - Fix so reflectances can be derived from scalar inputs

In this release 2 pull requests were closed.


## Version v0.10.4 (2020/12/07)


### Pull Requests Merged

#### Features added

* [PR 125](https://github.com/pytroll/pyspectral/pull/125) - Add GitHub ci support

In this release 1 pull request was closed.


## Version v0.10.3 (2020/12/04)

### Issues Closed

* [Issue 89](https://github.com/pytroll/pyspectral/issues/89) - GK2A AMI RSR wavelengths are reversed

In this release 1 issue was closed.


## Version v0.10.2 (2020/11/20)

### Issues Closed

* [Issue 122](https://github.com/pytroll/pyspectral/issues/122) - Pyspectral incompatible with h5py=3.1.0 ([PR 123](https://github.com/pytroll/pyspectral/pull/123) by [@pnuu](https://github.com/pnuu))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 124](https://github.com/pytroll/pyspectral/pull/124) - Refactor the rsr-reader and add more test coverage ([122](https://github.com/pytroll/pyspectral/issues/122))
* [PR 123](https://github.com/pytroll/pyspectral/pull/123) - Add a utility function to decode HDF5 strings ([122](https://github.com/pytroll/pyspectral/issues/122))
* [PR 120](https://github.com/pytroll/pyspectral/pull/120) - Fix scale of AGRI response values
* [PR 118](https://github.com/pytroll/pyspectral/pull/118) - Update documentation with new satellites / sensors and correct typos

#### Features added

* [PR 124](https://github.com/pytroll/pyspectral/pull/124) - Refactor the rsr-reader and add more test coverage ([122](https://github.com/pytroll/pyspectral/issues/122))
* [PR 123](https://github.com/pytroll/pyspectral/pull/123) - Add a utility function to decode HDF5 strings ([122](https://github.com/pytroll/pyspectral/issues/122))
* [PR 121](https://github.com/pytroll/pyspectral/pull/121) - Fix codefactor issues and appveyor testing
* [PR 119](https://github.com/pytroll/pyspectral/pull/119) - Add wavelength rangefinder

#### Documentation changes

* [PR 118](https://github.com/pytroll/pyspectral/pull/118) - Update documentation with new satellites / sensors and correct typos

In this release 9 pull requests were closed.


## Version v0.10.1 (2020/10/06)

### Issues Closed

* [Issue 112](https://github.com/pytroll/pyspectral/issues/112) - Do not cut NIR reflectance with a single threshold ([PR 113](https://github.com/pytroll/pyspectral/pull/113))
* [Issue 111](https://github.com/pytroll/pyspectral/issues/111) - Error in equation in documentation ([PR 117](https://github.com/pytroll/pyspectral/pull/117))

In this release 2 issues were closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 117](https://github.com/pytroll/pyspectral/pull/117) - Fix documentation error in SI unit conversion ([111](https://github.com/pytroll/pyspectral/issues/111))

#### Features added

* [PR 116](https://github.com/pytroll/pyspectral/pull/116) - Skip python2 support
* [PR 113](https://github.com/pytroll/pyspectral/pull/113) - Separate masking and Sun zenith angle correction ([112](https://github.com/pytroll/pyspectral/issues/112))
* [PR 110](https://github.com/pytroll/pyspectral/pull/110) - Add bandname mapping for slstr

#### Documentation changes

* [PR 117](https://github.com/pytroll/pyspectral/pull/117) - Fix documentation error in SI unit conversion ([111](https://github.com/pytroll/pyspectral/issues/111))

In this release 5 pull requests were closed.



## Version v0.10.0 (2020/06/24)

### Issues Closed

* [Issue 96](https://github.com/pytroll/pyspectral/issues/96) - Spectral response function for SLSTR on Sentinel 3B ([PR 104](https://github.com/pytroll/pyspectral/pull/104))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 105](https://github.com/pytroll/pyspectral/pull/105) - Use original channel data on the night side for NIR emissive

#### Features added

* [PR 109](https://github.com/pytroll/pyspectral/pull/109) - add more realistic METimage RSRs
* [PR 108](https://github.com/pytroll/pyspectral/pull/108) - Add option to specify sun-zenith angle threshold applied
* [PR 107](https://github.com/pytroll/pyspectral/pull/107) - Add support for FCI
* [PR 105](https://github.com/pytroll/pyspectral/pull/105) - Use original channel data on the night side for NIR emissive
* [PR 104](https://github.com/pytroll/pyspectral/pull/104) - Updated Zenodo link for addition of SLSTR on Sentinel 3B ([96](https://github.com/pytroll/pyspectral/issues/96))

In this release 5 pull requests were closed.



## Version v0.9.5 (2020/02/04)

### Issues Closed

* [Issue 101](https://github.com/pytroll/pyspectral/issues/101) - Getting the near infrared reflectance of a viirs scene crashes. ([PR 102](https://github.com/pytroll/pyspectral/pull/102))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 103](https://github.com/pytroll/pyspectral/pull/103) - Fix '-' (minus) sign in math string
* [PR 102](https://github.com/pytroll/pyspectral/pull/102) - Fix round returning a float ([101](https://github.com/pytroll/pyspectral/issues/101), [101](https://github.com/pytroll/pyspectral/issues/101))

#### Documentation changes

* [PR 103](https://github.com/pytroll/pyspectral/pull/103) - Fix '-' (minus) sign in math string
* [PR 100](https://github.com/pytroll/pyspectral/pull/100) - Updated the documentation of inverse Planck function for broad channels

In this release 4 pull requests were closed.


## Version v0.9.4 (2019/12/30)


### Pull Requests Merged

#### Bugs fixed

* [PR 99](https://github.com/pytroll/pyspectral/pull/99) - Fix Read The Doc pages - does not build at the moment

#### Features added

* [PR 97](https://github.com/pytroll/pyspectral/pull/97) - Fix NIR computations to be more lenient towards dask arrays

#### Documentation changes

* [PR 99](https://github.com/pytroll/pyspectral/pull/99) - Fix Read The Doc pages - does not build at the moment

In this release 3 pull requests were closed.


## Version v0.9.3 (2019/12/06)

### Issues Closed

* [Issue 92](https://github.com/pytroll/pyspectral/issues/92) - Fails to pull from Github because of a git-lfs quota limit ([PR 93](https://github.com/pytroll/pyspectral/pull/93))
* [Issue 90](https://github.com/pytroll/pyspectral/issues/90) - CREFL rayleigh Goes-16 ABI L1B

In this release 2 issues were closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 95](https://github.com/pytroll/pyspectral/pull/95) - Adapt for later versions of TQDM
* [PR 93](https://github.com/pytroll/pyspectral/pull/93) - Abandon gitlfs ([92](https://github.com/pytroll/pyspectral/issues/92))
* [PR 87](https://github.com/pytroll/pyspectral/pull/87) - Fix doc strings (flake8 complaints).

#### Features added

* [PR 95](https://github.com/pytroll/pyspectral/pull/95) - Adapt for later versions of TQDM
* [PR 88](https://github.com/pytroll/pyspectral/pull/88) - Feature pytest
* [PR 87](https://github.com/pytroll/pyspectral/pull/87) - Fix doc strings (flake8 complaints).
* [PR 86](https://github.com/pytroll/pyspectral/pull/86) - Switch from versioneer

#### Documentation changes

* [PR 94](https://github.com/pytroll/pyspectral/pull/94) - Add the atm correction paper reference
* [PR 87](https://github.com/pytroll/pyspectral/pull/87) - Fix doc strings (flake8 complaints).

In this release 9 pull requests were closed.


## Version v0.9.2 (2019/10/03)

### Pull Requests Merged

#### Bugs fixed

* [PR 85](https://github.com/pytroll/pyspectral/pull/85) - Fix doc tests for r37 derivations
* [PR 84](https://github.com/pytroll/pyspectral/pull/84) - Add AMI channel aliases from Satpy

In this release 2 pull requests were closed.


## Version <RELEASE_VERSION> (2019/09/30)

### Issues Closed

### Pull Requests Merged

#### Features added

* [PR 83](https://github.com/pytroll/pyspectral/pull/83) - Fix for appveyor, using Daves custom branch&fork of ci-helpers
* [PR 82](https://github.com/pytroll/pyspectral/pull/82) - Add support for AMI on GEO-KOMPSAT-2A

In this release 2 pull requests were closed.


## Version <RELEASE_VERSION> (2019/08/30)

### Issues Closed

* [Issue 73](https://github.com/pytroll/pyspectral/issues/73) - Fix blackbody code to work with dask arrays ([PR 74](https://github.com/pytroll/pyspectral/pull/74))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 80](https://github.com/pytroll/pyspectral/pull/80) - Fix doc tests for python 2&3
* [PR 79](https://github.com/pytroll/pyspectral/pull/79) - Fix rsr zenodo version
* [PR 74](https://github.com/pytroll/pyspectral/pull/74) - Fix dask compatibility in blackbody functions ([73](https://github.com/pytroll/pyspectral/issues/73))

#### Features added

* [PR 78](https://github.com/pytroll/pyspectral/pull/78) - Add FY-3B VIRR and FY-3C VIRR RSRs
* [PR 77](https://github.com/pytroll/pyspectral/pull/77) - Add FY-4A AGRI support

In this release 5 pull requests were closed.


## Version <RELEASE_VERSION> (2019/06/07)

### Issues Closed

* [Issue 75](https://github.com/pytroll/pyspectral/issues/75) - 'download_luts' and 'download_rsr' functions always download files ([PR 76](https://github.com/pytroll/pyspectral/pull/76))

In this release 1 issue was closed.

### Pull Requests Merged

#### Features added

* [PR 76](https://github.com/pytroll/pyspectral/pull/76) - Feature download LUT files only if outdated ([75](https://github.com/pytroll/pyspectral/issues/75))

In this release 1 pull request was closed.

## Version <RELEASE_VERSION> (2019/04/29)

### Issues Closed

* [Issue 70](https://github.com/pytroll/pyspectral/issues/70) - Update yaml usage to work with pyyaml 5.1+ ([PR 71](https://github.com/pytroll/pyspectral/pull/71))
* [Issue 66](https://github.com/pytroll/pyspectral/issues/66) - Throws a warning about non-existing directory - storing/reading cached radiance-tb look-up-tables ([PR 67](https://github.com/pytroll/pyspectral/pull/67))
* [Issue 61](https://github.com/pytroll/pyspectral/issues/61) - can this program be used for user-defined sensor or rsr？ ([PR 62](https://github.com/pytroll/pyspectral/pull/62))
* [Issue 58](https://github.com/pytroll/pyspectral/issues/58) - Use dask instead of numpy masked arrays ([PR 59](https://github.com/pytroll/pyspectral/pull/59))

In this release 4 issues were closed.

### Pull Requests Merged

#### Features added

* [PR 71](https://github.com/pytroll/pyspectral/pull/71) - Fix yaml 5.1+ support with unsafe loading ([70](https://github.com/pytroll/pyspectral/issues/70), [70](https://github.com/pytroll/pyspectral/issues/70))
* [PR 69](https://github.com/pytroll/pyspectral/pull/69) - Feature rayleigh catch exception
* [PR 68](https://github.com/pytroll/pyspectral/pull/68) - Feaure metimage multiple detectors
* [PR 65](https://github.com/pytroll/pyspectral/pull/65) - Feature add metimage


In this release 4 pull requests were closed.


## Version <RELEASE_VERSION> (2019/04/09)

### Issues Closed

* [Issue 66](https://github.com/pytroll/pyspectral/issues/66) - Throws a warning about non-existing directory - storing/reading cached radiance-tb look-up-tables ([PR 67](https://github.com/pytroll/pyspectral/pull/67))
* [Issue 61](https://github.com/pytroll/pyspectral/issues/61) - can this program be used for user-defined sensor or rsr？ ([PR 62](https://github.com/pytroll/pyspectral/pull/62))
* [Issue 58](https://github.com/pytroll/pyspectral/issues/58) - Use dask instead of numpy masked arrays ([PR 59](https://github.com/pytroll/pyspectral/pull/59))

In this release 3 issues were closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 67](https://github.com/pytroll/pyspectral/pull/67) - Bugfix tb2rad lut caching ([66](https://github.com/pytroll/pyspectral/issues/66))
* [PR 64](https://github.com/pytroll/pyspectral/pull/64) - Fix interp function in rayleigh correction to be serializable


#### Features added

* [PR 59](https://github.com/pytroll/pyspectral/pull/59) - Daskify NIR reflectance calculations ([58](https://github.com/pytroll/pyspectral/issues/58))

In this release 2 pull requests were closed.


## Version <RELEASE_VERSION> (2018/12/04)

### Issues Closed

* [Issue 38](https://github.com/pytroll/pyspectral/issues/38) - Download RSR data in vain

In this release 1 issue was closed.

### Pull Requests Merged

#### Features added

* [PR 60](https://github.com/pytroll/pyspectral/pull/60) - Fix readthedocs

In this release 1 pull request was closed.


## Version <RELEASE_VERSION> (2018/11/30)

### Issues Closed

* [Issue 50](https://github.com/pytroll/pyspectral/issues/50) - Re-download of RSR files ([PR 56](https://github.com/pytroll/pyspectral/pull/56))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 53](https://github.com/pytroll/pyspectral/pull/53) - Fix masking of calculated NIR reflectances

#### Features added

* [PR 57](https://github.com/pytroll/pyspectral/pull/57) - Script cleanup and document
* [PR 56](https://github.com/pytroll/pyspectral/pull/56) - Rsr download fix ([50](https://github.com/pytroll/pyspectral/issues/50))

In this release 3 pull requests were closed.


## Version <RELEASE_VERSION> (2018/11/30)

### Issues Closed

* [Issue 50](https://github.com/pytroll/pyspectral/issues/50) - Re-download of RSR files ([PR 56](https://github.com/pytroll/pyspectral/pull/56))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 53](https://github.com/pytroll/pyspectral/pull/53) - Fix masking of calculated NIR reflectances

#### Features added

* [PR 57](https://github.com/pytroll/pyspectral/pull/57) - Script cleanup and document
* [PR 56](https://github.com/pytroll/pyspectral/pull/56) - Rsr download fix ([50](https://github.com/pytroll/pyspectral/issues/50))

In this release 3 pull requests were closed.
