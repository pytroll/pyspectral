Example with SEVIRI data
------------------------

Let us try calculate the 3.9 micron reflectance for Meteosat-10:

.. doctest::

  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> from pyspectral.near_infrared_reflectance import Calculator
  >>> refl39 = Calculator('Meteosat-10', 'seviri', 'IR3.9')
  >>> print('%4.3f' %refl39.reflectance_from_tbs(sunz, tb3, tb4))
  0.555

You can also provide the in-band solar flux from outside when calculating the
reflectance, saving a few milliseconds per call::

  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005)
  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> seviri = RelativeSpectralResponse('Meteosat-10', 'seviri')
  >>> sflux = solar_irr.inband_solarflux(seviri.rsr['IR3.9'])
  >>> refl39 = Calculator('Meteosat-10', 'seviri', 'IR3.9', solar_flux=sflux)
  >>> print('%4.3f' %refl39.reflectance_from_tbs(sunz, tb3, tb4))
  0.555
