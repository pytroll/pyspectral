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

You can download the source code from github_::

  $> git clone git://github.com/adybbroe/pyspectral.git

and then run::

  $> python setup.py install

or, if you want to hack the package::

  $> python setup.py develop


Usage
-----

A simple use case:

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
the Aqua MODIS 3.7 micron band:


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

