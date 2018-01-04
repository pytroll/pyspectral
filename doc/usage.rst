Usage
-----

Get the spectral responses for Sentinel-3A OLCI (and turn on debugging to see
more info on what is being done behind the curtan):

  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> from pyspectral.utils import debug_on
  >>> debug_on()
  >>> olci = RelativeSpectralResponse('Sentinel-3A', 'olci')

You will see that if you haven't run this kind of code before, pyspectral will
download the spectral responses for all satellites supported from Zenodo.


Now, you can work with the data as you wish, make some simple plot for instance:

  >>> print("{0}".format(olci.band_names))
  ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20']
  >>> print("Central wavelength = {wvl:7.6f}".format(wvl=olci.rsr['ch1']['det-1']['central_wavelength']))
  Central wavelength = 0.400123
  >>> import matplotlib.pyplot as plt
  >>> dummy = plt.figure(figsize=(10, 5))
  >>> import numpy as np
  >>> resp = np.ma.masked_less_equal(olci.rsr['ch1']['det-1']['response'], 0.015)
  >>> wvl = np.ma.masked_array(olci.rsr['ch1']['det-1']['wavelength'], resp.mask)
  >>> dummy = plt.plot(wvl.compressed(), resp.compressed())
  >>> plt.show() # doctest: +SKIP

  .. image:: _static/olci_ch1.png


A simple use case:

  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> modis = RelativeSpectralResponse('EOS-Aqua', 'modis')
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.005)
  >>> sflux = solar_irr.inband_solarflux(modis.rsr['20'])
  >>> print("Solar flux over Band: {sflux}".format(sflux=round(sflux, 6)))
  Solar flux over Band: 2.002928

And, here is how to derive the solar reflectance (removing the thermal part) of
the Aqua MODIS 3.7 micron band::

  >>> from pyspectral.near_infrared_reflectance import Calculator
  >>> import numpy as np
  >>> sunz = 80.
  >>> tb3 = 290.0
  >>> tb4 = 282.0
  >>> refl37 = Calculator('EOS-Aqua', 'modis', '20', detector='det-1', solar_flux=2.0029281634299041)
  >>> print("Reflectance = {r:7.6f}".format(r=np.ma.round(refl37.reflectance_from_tbs(sunz, tb3, tb4), 6)))
  Reflectance = 0.251249


And, here is how to derive the rayleigh (with additional optional aerosol
absorption) contribution in a short wave band:

  >>> from pyspectral import rayleigh
  >>> rcor = rayleigh.Rayleigh('GOES-16', 'abi')
  >>> import numpy as np
  >>> sunz = np.array([[50., 60.], [51., 61.]])
  >>> satz = np.array([[40., 50.], [41., 51.]])
  >>> azidiff = np.array([[160, 160], [160, 160]])
  >>> blueband =  np.array([[0.1, 0.15], [0.11, 0.16]])
  >>> print(rcor.get_reflectance(sunz, satz, azidiff, 'ch2', blueband))
  [[ 2.01927932  3.20415785]
   [ 2.08904394  3.41731944]]


