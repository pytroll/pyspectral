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
