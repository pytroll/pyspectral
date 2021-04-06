Example with SEVIRI data
------------------------

Let us try calculate the 3.9 micron reflectance for Meteosat-10:

.. doctest::

  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> from pyspectral.near_infrared_reflectance import Calculator
  >>> refl39 = Calculator('Meteosat-10', 'seviri', 'IR3.9')
  >>> print('{refl:4.3f}'.format(refl=refl39.reflectance_from_tbs(sunz, tb3, tb4)[0]))
  0.555

You can also provide the in-band solar flux from outside when calculating the
reflectance, saving a few milliseconds per call::

  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005)
  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> seviri = RelativeSpectralResponse('Meteosat-10', 'seviri')
  >>> sflux = solar_irr.inband_solarflux(seviri.rsr['IR3.9'])
  >>> refl39 = Calculator('Meteosat-10', 'seviri', 'IR3.9', solar_flux=sflux)
  >>> print('{refl:4.3f}'.format(refl=refl39.reflectance_from_tbs(sunz, tb3, tb4)[0]))
  0.555

By default the data are masked outside the default Sun zenith-angle (SZA) correction limit (85.0 degrees).
The masking can be adjusted via `masking_limit` keyword argument to `Calculator`, and turned of by
defining `Calculator(..., masking_limit=None)`. The SZA limit can be adjusted via `sunz_threshold` keyword argument:
`Calculator(..., sunz_threshold=88.0)`.

Integration with SatPy
^^^^^^^^^^^^^^^^^^^^^^
The SatPy_ package integrates PySpectral_ so that it is very easy with only a
very few lines of code to make RGB images with the 3.9 reflectance as one of
the bands. Head to the `PyTroll gallery`_ pages for examples. SatPy_ for instance
has a  *snow* RGB using the 0.8 micron, the 1.6 micron and the 3.9 micron
reflectance derived using PySpectral_.


.. _PySpectral: http://github.com/pytroll/pyspectral
.. _SatPy: http://www.github.com/pytroll/satpy
.. _PyOrbital: http://www.github.com/pytroll/pyorbital
.. _`PyTroll gallery`: http://pytroll.github.io/gallery.html
