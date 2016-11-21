.. Pyspectral documentation master file, created by
   sphinx-quickstart on Tue Oct 15 13:31:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to Pyspectral's documentation!
======================================

.. figure:: _static/msg_daysolar_rgb_20131129_1100_overlay_small_thumb.png 
   :align: left

.. figure:: _static/msg_day_microphysics_summer_rgb_20131129_1100_overlay_small_thumb.png
   


Pyspectral is a package to read meteorological satellite instrument relative
spectral response functions and solar irradiance spectra, and e.g. provide
functionality to derive the in-band solar flux for various satellite sensors.
The sensors in question are first of all VIIRS, MODIS, AVHRR and SEVIRI.

The source code of the module can be found on the github_ page.

With pyspectral and mpop_ it is possible to make RGB colour composites like the
SEVIRI `day solar`_ or the `day microphysical`_ RGB composites according to the
`MSG Interpretation Guide`_ (EUMETSAT_).


.. _`EUMETSAT`: http://www.eumetsat.int/
.. _`day solar`: _static/msg_daysolar_rgb_20131129_1100_overlay_small.png
.. _`day microphysical`: _static/msg_day_microphysics_summer_rgb_20131129_1100_overlay_small.png
.. _github: http://github.com/pytroll/pyspectral
.. _mpop: http://www.github.com/pytroll/mpop
.. _MSG Interpretation Guide: http://oiswww.eumetsat.org/WEBOPS/msg_interpretation/index.php 


.. toctree::
   :maxdepth: 2

   installation
   usage
   seviri_example
   37_reflectance
   rayleigh_correction
   rad_definitions
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

