.. Pyspectral documentation master file, created by
   sphinx-quickstart on Tue Oct 15 13:31:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pyspectral's documentation!
======================================

pyspectral is a package to read meteorological satellite instrument relative
spectral response functions and solar irradiance spectra, and e.g. provide
functionality to derive the in-band solar flux for various satellite sensors.
The sensors in question are first of all VIIRS, MODIS, AVHRR and SEVIRI.


The source code of the module can be found on the github_ page.

.. _github: http://github.com/adybbroe/pyspectral


Contents:

.. toctree::
   :maxdepth: 2


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


Usage
-----

Copy the template file *pyspectral.cfg_template* to *pyspectral.cfg* and place
it in a directory as you please. Set the environment variable PSP_CONFIG_FILE
pointing to the file. E.g.::
 
  $> PSP_CONFIG_FILE=/home/a000680/pyspectral.cfg; export PSP_CONFIG_FILE

A simple use case::

  >>> from pyspectral.rsr_read import RelativeSpectralResponse
  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> modis = RelativeSpectralResponse('eos', 2, 'modis')
  >>> modis.read(channel='20', scale=0.001)
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.005)
  >>> solar_irr.read()
  >>> sflux = solar_irr.solar_flux_over_band(modis.rsr)
  >>> print("Solar flux over Band: ", sflux)
  ('Solar flux over Band: ', 1.9674582420093827)

And, here is how to derive the solar reflectance (removing the thermal part) of
the Aqua MODIS 3.7 micron band::

  >>> from pyspectral.nir_reflectance import reflectance
  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> print reflectance(modis.rsr, sunz, tb3, tb4)
  [ 0.25171415]






Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

