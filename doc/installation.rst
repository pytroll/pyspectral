Installation
------------

Pyspectral reads relative spectral response functions for various satellite
sensors. The spectral response data are stored in various formats (usually
ascii) and using various standards. These data are usually available at the
satellite agencies responsible for the instrument in question. That is for
example EUMETSAT, NOAA, NASA, JMA and CMA. The Global Space-based
Inter-Calibration System (GSICS_) Coordination Center (GCC_) holds a place with
links to several relevant `instrument response data`_.

First download the spectral responses needed and unpack the data if needed, and
provide the path to the data in the configuration file *pyspectral.cfg*. For
SEVIRI on Meteosat download the data from eumetsat_ and unzip the Excel file.

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
