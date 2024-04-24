Installation
------------

Installation of the latest stable version is always done using:: 

  $>  pip install pyspectral

Some static data are part of the package. Downloading of this data is handled
automagically by the software when data are needed. However, the data can also
be downloaded manually once and for all by calling dedicated download
scripts. The latter is helpful when running PySpectral in an operational
environment. See further below on how the static data downloads are handled.

You can also choose to download the PySpectral source code from github_::

  $> git clone git://github.com/pytroll/pyspectral.git

and then run::

  $> python setup.py install

or, if you want to hack the package::

  $> python setup.py develop


Static data
-----------

PySpectral make use of and requires the access to two different kinds of static
ancillary data sets. First, relative spectral responses for a large number of
satellite imaging sensors are available in a unified hdf5 format. Secondly,
PySpectral comes with a set of Look-Up-Tables (LUTs) for the atmospheric
correction in the short wave spectral range.

Both these datasets downloads automagically from `zenodo.org`_ when needed.

On default these static data will reside in the platform specific standard
destination for storing user data, via the use of the platformdirs_ package. On
Linux this will be under *~/.local/share/pyspectral*. See further down.


The spectral response data 
^^^^^^^^^^^^^^^^^^^^^^^^^^

PySpectral reads relative spectral response functions for various satellite
sensors. The original agency specific spectral response data are stored in
various different formats (e.g. ascii, excel, or netCDF), with varying levels of
detailed information available, and usually not following any agreed
international standard.

These data are often available at the satellite agencies responsible for the
instrument in question. That is for example EUMETSAT, NOAA, NASA, JMA and
CMA. The Global Space-based Inter-Calibration System (GSICS_) Coordination
Center (GCC_) holds a place with links to several relevant `instrument response
data`_. But far from all data are available through that web-site.

Therefore, in order to make life easier for the *PySpectral* user we have
defined one common internal HDF5 format. That way it is also easy to add
support for new instruments. Currently the relative spectral responses for the
following sensors are included:

 * Suomi-NPP and NOAA-20 VIIRS
 * All of the NOAA/TIROS-N and Metop AVHRRs
 * Terra/Aqua MODIS
 * Meteosat 8-11 SEVIRI
 * Sentinel-3A/3B SLSTR and OLCI
 * Envisat AATSR
 * GOES-16/17 ABI
 * Himawari-8/9 AHI
 * Sentinel-2 A&B MSI
 * Landsat-8 OLI
 * Geo-Kompsat-2A / AMI
 * Fengyun-4A / AGRI

The data are automagically downloaded and installed when needed. But if you
need to specifically retrieve the data independently the data are available
from the `pyspectral rsr`_ repository and can be downloaded using a script that
comes with *PySpectral*. For instance, to download the data into the default
directory:


.. code::
   
   python ~/.local/bin/download_rsr.py

   
Instead if you want to download the data to a specific directory and
using verbose mode (to get some log information on the screen):

.. code::
   
   python ~/.local/bin/download_rsr.py -v -o /tmp
   

It is still also possible to download the original spectral responses from the
various satellite operators instead and generate the internal HDF5 formatted
files yourself. However, this should normally never be needed. (For SEVIRI on
Meteosat download the data from eumetsat_ and unzip the Excel file.)


Look-Up-Tables for atmospheric correction in the SW spectral range
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Look-Up-Tables (LUTs) with simulated black surface top of atmosphere
reflectances over the :math:`400-600 nm` wavelength spectrum for various
aerosol distributions and a set of standard atmospheres for varying
sun-satellite viewing are available in HDF5 on `zenodo.org`_. The LUTs are
downloaded automagically when needed and placed in the same directory structure
as the spectral response data (see above). The data can also be downloaded
manually using a dedicated download script. To download all LUTs you can do
like this:

  .. code::
   
   python ~/.local/bin//download_atm_correction_luts.py


If you only need LUTs for a few aerosol distributions, for example *desert
aerosols* and *marine clean aerosols* (and using verbose mode to get some log
info on the screen):

  .. code::
   
   python ~/.local/bin//download_atm_correction_luts.py -a desert_aerosol marine_clean_aerosol -v
   


Configuration file
^^^^^^^^^^^^^^^^^^

A default configuration file *pyspectral.yaml* is installed automatically and
being part of the package under the *etc* directory. In many cases the default
settings will allow one to do all what is needed. However, it can easily be
overwritten by making your own copy and set an environment variable pointing to
this configuration file, as e.g.::

  $> PSP_CONFIG_FILE=/home/a000680/pyspectral.yaml; export PSP_CONFIG_FILE

So, in case you want to download the internal *PySpectral* formatted relative
spectral responses as well as the atmospheric correction LUTs once and for all,
and keep them somewhere else. Change the configuration in *pyspectral.yaml* so
it looks something like this:

.. code-block:: ini

   rsr_dir = /path/to/internal/rsr_data
   rayleigh_dir = /path/to/rayleigh/correction/luts
   download_from_internet = True

Then download the data:

  .. code::
   
   python ~/.local/bin/download_rsr.py

  .. code::
   
   python ~/.local/bin//download_atm_correction_luts.py


And then adjust the *pyspectral.yaml* so data downloading will not be attempted anymore:

.. code-block:: ini

   rsr_dir = /path/to/internal/rsr_data
   rayleigh_dir = /path/to/rayleigh/correction/luts
   download_from_internet = False


.. _pyspectral rsr: https://zenodo.org/record/1012412/files/pyspectral_rsr_data.tgz
.. _eumetsat: http://www.eumetsat.int/website/wcm/idc/idcplg?IdcService=GET_FILE&dDocName=ZIP_MSG_SEVIRI_SPEC_RES_CHAR&RevisionSelectionMethod=LatestReleased&Rendition=Web
.. _GSICS: http://www.wmo.int/pages/prog/sat/GSICS/
.. _GCC: http://www.star.nesdis.noaa.gov/smcd/GCC/index.php
.. _instrument response data: http://www.star.nesdis.noaa.gov/smcd/GCC/instrInfo-srf.php
.. _github: http://github.com/pytroll/pyspectral
.. _platformdirs: https://github.com/platformdirs/platformdirs
.. _zenodo.org: https://zenodo.org
