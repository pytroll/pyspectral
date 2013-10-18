
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

  >>> from pyspectral.nir_reflectance import Calculator
  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> refl37 = Calculator(modis.rsr, solar_flux=sflux)
  >>> print refl37.reflectance_from_tbs(sunz, tb3, tb4)
  0.258119312599
