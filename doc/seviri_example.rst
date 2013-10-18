Example with SEVIRI data
------------------------

Let us try calculate the 3.9 micron reflectance for Meteosat-10:

.. doctest::

  >>> from pyspectral.seviri_rsr import read
  >>> seviri = read()
  >>> rsr = {'wavelength': seviri['IR3.9']['wavelength'], 
             'response': seviri['IR3.9']['met10']['95']}
  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> from pyspectral.nir_reflectance import Calculator
  >>> refl39 = Calculator(rsr)
  >>> print refl39.reflectance_from_tbs(sunz, tb3, tb4)
  0.554324450696

You can also provide the in-band solar flux from outside when calculating the
reflectance, saving a few milliseconds per call::

  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005)
  >>> solar_irr.read()
  >>> sflux = solar_irr.solar_flux_over_band(rsr)
  >>> refl39 = Calculator(rsr, solar_flux=sflux)
  >>> print refl39.reflectance_from_tbs(sunz, tb3, tb4)
  0.554324450696
