
* First download the latest pyspectral-rsr data archive from Zenodo: Search
  zenodo for "Satellite Sensor Relative Spectral Response data", and select the
  latest version and click the download button at the bottom of the page.

* Unpack it into an empty directory

* Add you new HDF5 RSR data file into the same directory

* Bump the version tag stored in the PYSPECTRAL_RSR_VERSION file

* Update the CHANGELOG_RSR_DATA.rst in the pyspectral code with a description
  of the new RSR data.

* Make a new tar file of the content of the directory just updated. E.g.:
    %> tar cvzf ../pyspectral_rsr_data.tgz rsr_* PYSPECTRAL_RSR_VERSION

* Upload the new tar file to Zenodo: Click "New version". Then click "Upload files". Upload the tarfile.

* Update the author list accordingly

* Update the description field with the changelog. Take the changelog
  description just added above in CHANGELOG_RSR_DATA.rst and paste on Zenodo.

* Write the version tag (e.g. v1.6.2) in the "Version" field

* Click the "Preview" at the top right and check the release. Then go back, and
  click "Publish" when satisfied.

* Once ready, get the download link and upgrade the link in the
  pyspectral/utils.py module accordingly. Also upgrade the version tag there.

* Update the Pyspectral on github (make a new PR) and make a new release.
