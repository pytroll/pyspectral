Usage
-----

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


And, here is how to derive the rayleigh (with additional optional aerosol absorption) contribution in a short wave band::

  >>> from pyspectral import rayleigh
  >>> rcor = rayleigh.Rayleigh('GOES-16', 'abi')
  >>> import numpy as np
  >>> sunz = np.array([[50., 60.], [51., 61.]])
  >>> satz = np.array([[40., 50.], [41., 51.]])
  >>> azidiff = np.array([[160, 160], [160, 160]])
  >>> blueband =  np.array([[0.1, 0.15], [0.11, 0.16]])
  >>> print rcor.get_reflectance(sunz, satz, azidiff, 'ch2', blueband)
  [[ 3.44474971  5.14612533]
   [ 3.56880351  5.39811687]]
