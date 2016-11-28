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
Among the sensors supported are VIIRS, MODIS, AVHRR, SEVIRI, AHI (Himawari).
Since version 0.3.0 it is also possible to apply atmospheric (Rayleigh
scattering and aerosol absorption) correction in the 400 to 800 nanometer
spectral range. This allows for the atmospheric correction of true color
imagery of any sensor provided it has the necessary bands in this spectral
range (e.g. MODIS, VIIRS and AHI).

The source code of the module can be found on the github_ page.

With pyspectral and mpop_ (or satpy_) it is possible to make RGB colour
composites like the SEVIRI `day solar`_ or the `day microphysical`_ RGB
composites according to the `MSG Interpretation Guide`_ (EUMETSAT_). Also with
mpop_ and satpy_ integration it is possible to make Rayleigh corrected true
color imagery.

.. _`EUMETSAT`: http://www.eumetsat.int/
.. _`day solar`: _static/msg_daysolar_rgb_20131129_1100_overlay_small.png
.. _`day microphysical`: _static/msg_day_microphysics_summer_rgb_20131129_1100_overlay_small.png
.. _github: http://github.com/pytroll/pyspectral
.. _mpop: http://www.github.com/pytroll/mpop
.. _satpy: http://www.github.com/pytroll/satpy
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

