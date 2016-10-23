Installation
------------

Pyspectral reads relative spectral response functions for various satellite
sensors. The spectral response data are stored in various formats (usually
ascii) and using various standards. These data are usually available at the
satellite agencies responsible for the instrument in question. That is for
example EUMETSAT, NOAA, NASA, JMA and CMA. The Global Space-based
Inter-Calibration System (GSICS_) Coordination Center (GCC_) holds a place with
links to several relevant `instrument response data`_.


Get the static data 
^^^^^^^^^^^^^^^^^^^ 
All these instrument relative spectral response data are stored in different
formats with varying levels of detailed information available. So, in order to
make life easier for the pyspectral user we have defined one common internal
hdf5 format. That way it is also easy to add support for new
instruments. Currently the relative spectral reponses for Suomi-NPP VIIRS, most
of the NOAA and Metop AVHRRs, Terra/Aqua MODIS and Meteosat 8-11 SEVIRI are
available. The data can be retrieved from the `pyspectral rsr`_
repository. (The md5sum of this gzipped tar file is 39449d005100efc9a17d2762dd5b5364).

It is still possible to download the original spectral responses from the
various satellite operators instead and generate the internal hdf5 formatet
files yourself. For SEVIRI on Meteosat download the data from eumetsat_ and
unzip the Excel file.

Download data and install
^^^^^^^^^^^^^^^^^^^^^^^^^
So, first download the spectral responses and unpack the data if needed, and
provide the path to the data in the configuration file *pyspectral.cfg*.
A template *pyspectral.cfg_template* is located in *pyspectral/etc*.

Here is an example using the *pyspectral* internal hdf5 format::

  $> cd /path/to/internal/rsr_data
  $> wget https://dl.dropboxusercontent.com/u/37482654/pyspectral_rsr_data.tgz
  $> tar xvzf pyspectral_rsr_data.tgz

In the *pyspectral.cfg* it may look like this:

.. code-block:: ini

   [general]
   rsr_dir = /path/to/internal/rsr_data



.. _pyspectral rsr: https://dl.dropboxusercontent.com/u/37482654/pyspectral_rsr_data.tgz
.. _eumetsat: http://www.eumetsat.int/website/wcm/idc/idcplg?IdcService=GET_FILE&dDocName=ZIP_MSG_SEVIRI_SPEC_RES_CHAR&RevisionSelectionMethod=LatestReleased&Rendition=Web
.. _GSICS: http://www.wmo.int/pages/prog/sat/GSICS/
.. _GCC: http://www.star.nesdis.noaa.gov/smcd/GCC/index.php
.. _instrument response data: http://www.star.nesdis.noaa.gov/smcd/GCC/instrInfo-srf.php


You can download the pyspectral source code from github_::

  $> git clone git://github.com/adybbroe/pyspectral.git

and then run::

  $> python setup.py install

or, if you want to hack the package::

  $> python setup.py develop


.. _github: http://github.com/adybbroe/pyspectral
