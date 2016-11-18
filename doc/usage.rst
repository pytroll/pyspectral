Usage
-----

Copy the template file *pyspectral.cfg_template* to *pyspectral.cfg* and place
it in a directory as you please. Set the environment variable PSP_CONFIG_FILE
pointing to the file. E.g.::
 
  $> PSP_CONFIG_FILE=/home/a000680/pyspectral.cfg; export PSP_CONFIG_FILE

A simple use case::

  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> modis = RelativeSpectralResponse('EOS-Aqua', 'modis')
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.005)
  >>> sflux = solar_irr.inband_solarflux(modis.rsr['20'])
  >>> print("Solar flux over Band: ", sflux)
  ('Solar flux over Band: ', 2.0029281634299037)

And, here is how to derive the solar reflectance (removing the thermal part) of
the Aqua MODIS 3.7 micron band::

  >>> from pyspectral.near_infrared_reflectance import Calculator
  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> refl37 = Calculator('EOS-Aqua', 'modis', '20', detector='det-1', solar_flux=2.0029281634299041)
  >>> print refl37.reflectance_from_tbs(sunz, tb3, tb4)
  0.251249064103
