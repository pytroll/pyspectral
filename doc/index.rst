.. Pyspectral documentation main file, created by
   sphinx-quickstart on Tue Oct 15 13:31:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to Pyspectral's documentation!
======================================

.. figure:: _static/pyspectral_header_montage.png


Given a passive sensor on a meteorological satellite PySpectral provides the
relative spectral response (rsr) function(s) and offers some basic
operations like convolution with the solar spectrum to derive the in band solar
flux for instance. The focus is imaging sensors like AVHRR, VIIRS, MODIS, ABI,
AHI and SEVIRI. But more sensors are included and if others are needed
they can be easily added. With PySpectral it is possible to derive the
reflective and emissive parts of the signal observed in any NIR band around 3-4
microns where both passive terrestrial emission and solar backscatter mix the
information received by the satellite. Furthermore PySpectral allows correcting
true color imagery for background (climatological) Rayleigh scattering and aerosol
absorption.

The source code can be found on the github_ page.

With PySpectral and SatPy_ (or previously mpop_) it is possible to make RGB colour
composites like the SEVIRI `day solar`_ or the `day microphysical`_ RGB
composites according to the `MSG Interpretation Guide`_ (EUMETSAT_). Also with
SatPy_ integration it is possible to make atmosphere corrected true
color imagery.

.. _`EUMETSAT`: http://www.eumetsat.int/
.. _`day solar`: _static/msg_daysolar_rgb_20131129_1100_overlay_small.png
.. _`day microphysical`: _static/msg_day_microphysics_summer_rgb_20131129_1100_overlay_small.png
.. _github: http://github.com/pytroll/pyspectral
.. _mpop: http://www.github.com/pytroll/mpop
.. _SatPy: http://www.github.com/pytroll/satpy
.. _MSG Interpretation Guide: https://resources.eumetrain.org/IntGuide/ 


.. toctree::
   :maxdepth: 2

   platforms_supported
   installation
   usage
   rsr_plotting
   seviri_example
   rad_definitions
   37_reflectance
   rayleigh_correction
   rsr_formatting
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

