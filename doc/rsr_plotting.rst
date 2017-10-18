Simple plotting of spectral responses
-------------------------------------

Plot VIIRS spectral responses (detector 1 only) for band M10 on JPSS-1 and Suomi-NPP:

.. code::
   
   python composite_rsr_plot.py -p NOAA-20 Suomi-NPP -s viirs -b M10

.. image:: _static/rsr_band_M10.png
           

Plot relative spectral responses for the spectral channel closest to the
:math:`10.8 \mu m`  for several platforms and sensors:

.. code::
   
   python composite_rsr_plot.py --platform_name Himawari-8 GOES-16 Meteosat-10 EOS-Aqua Sentinel-3A Suomi-NPP NOAA-20 --sensor ahi abi seviri modis olci slstr viirs --wavelength 10.8

.. image:: _static/rsr_band_1080.png


           

