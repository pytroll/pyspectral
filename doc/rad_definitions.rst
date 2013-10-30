Some definitions
----------------

In radiation physics there is unfortunately several slightly different ways of
presenting the theory. For instance, there is no single custom on the mathematical
symbolism, and various different non SI-units are used in different situations. Here
we present just a few terms and definitions with relevance to Pyspectral, and
how to possible go from one common representation to another.


Symbols and definitions used in Pyspectral
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\lambda`                 |  Wavelength (in :math:`\mu m`)                                                         |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\nu = \frac{1}{\lambda}` | Wavenumber (in :math:`cm^{-1}`)                                                        |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\lambda_{c}`             | Central wavelength for a given band/channel (in :math:`\mu m`)                         |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\nu_{c}`                 | Central wavelength for a given band/channel (in :math:`cm^{-1}`)                       |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\Phi_{i}(\lambda)`       | Relative spectral response for band :math:`i` as a function of wavelength              |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`E_{\lambda}`             | Spectral irradiance at wavelength :math:`\lambda` (in :math:`W/m^2 \mu m^{-1}`)        |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`E_{\nu}`                 | Spectral irradiance at wavenumber :math:`\nu` (in :math:`W/m^2 (cm^{-1})^{-1}`)        |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`L_{\nu}`                 | Spectral radiance at wavenumber :math:`\nu` (in :math:`W/m^2 sr^{-1} (cm^{-1})^{-1}`)  |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`L_{\lambda}`             | Spectral radiance at wavelength :math:`\lambda` (in :math:`W/m^2 sr^{-1} \mu m^{-1}`)  |
  +---------------------------------+----------------------------------------------------------------------------------------+



Central wavelength and central wavenumber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The central wavelength for a given spectral band (:math:`i`) of a satellite sensor is defined as:

.. math::

    {\lambda_c}_i = \frac{\int_0^\infty \Phi_{i}(\lambda) \lambda \mathrm{d}\lambda}
    {\int_0^\infty \Phi_{i}(\lambda) \mathrm{d}\lambda}

Likewise the central wavenumber is:

.. math::

    {\nu_c}_i = \frac{\int_0^\infty \Phi_{i}(\nu) \nu \mathrm{d}\nu}
    {\int_0^\infty \Phi_{i}(\nu) \mathrm{d}\nu}

And since :math:`\nu = 1/\lambda`, we can express the central wavenumber using
the spectral response function expressed in wavelength space, as:

.. math::

    {\nu_c}_i = \frac{\int_0^\infty \Phi_{i}(\lambda) \frac{1}{\lambda^{3}} \mathrm{d}\lambda}
    {\int_0^\infty \Phi_{i}(\lambda) \frac{1}{\lambda^{2}} \mathrm{d}\lambda}

And from this we see that in general :math:`\nu_c \neq 1/\lambda_c`. 

Taking SEVIRI as an example, and looking at the visible channel on Meteosat 8,
we see that this is indeed true:

  >>> from pyspectral.seviri_rsr import Seviri
  >>> seviri = Seviri()
  >>> print seviri.central_wavelength['VIS0.6']['met8']
  0.640215597159
  >>> seviri = Seviri(wavespace='wavenumber')
  >>> print seviri.central_wavenumber['VIS0.6']['met8']
  15682.623379
  >>> print 1./seviri.central_wavenumber['VIS0.6']['met8']*1e4
  0.637648418783


Spectral Irradiance
^^^^^^^^^^^^^^^^^^^

We denote the spectral irradiance :math:`E` which is a function of wavelength
or wavenumber, depending on what representation is used. In Pyspectral the aim
is to support both representations. The units are of course dependent of which
representation is used. 

In wavelength space we write :math:`E(\lambda)` and it is given in units of
:math:`W/m^2 \mu m^{-1}`.

In wavenumber space we write :math:`E(\nu)` and it is given in units of
:math:`W/m^2 (cm^{-1})^{-1}`.

To convert a spectral irradiance :math:`E_{\lambda_0}` at wavelengh
:math:`\lambda_0` to a spectral irradiance :math:`E_{\nu_0}` at wavenumber 
:math:`\nu_0 = 1/\lambda_0` the following relation applies:

.. math::

    E_\nu = E_\lambda \lambda^2

And if the units are not SI but rather given by the units shown above we have to account for a factor of 10 as:

.. math::

    E_\nu = {E_\lambda * \lambda^2 * 0.1}



TOA Solar irridiance and solar constant
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, the TOA solar irradiance in wavelength space:

  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005) 
  >>> print solar_irr.solar_constant()
  1366.0907968389995
  >>> solar_irr.plot('/tmp/solar_irradiance.png')

  .. image:: _static/solar_irradiance.png

The solar constant is in units of :math:`W/m^2`. Instead when expressing the
irradiance in wavenumber space using wavenumbers in units of :math:`cm^{-1}`
the solar flux is in units of :math:`mW/m^2`:

  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005, wavespace='wavenumber')
  >>> print solar_irr.solar_constant()
  1366077.16482
  >>> solar_irr.plot('/tmp/solar_irradiance_wnum.png')

  .. image:: _static/solar_irradiance_wnum.png



In-band solar irradiance and flux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The solar flux (SI unit :math:`\frac{W}{m^2}`) over a spectral sensor band can
be derived by convolving the top of atmosphere solar spectral irradiance and
the sensor relative spectral response. For band :math:`i`:

.. math::

    F_i = \int_0^\infty \Phi_{i}(\lambda) E(\lambda) \mathrm{d}\lambda 

where :math:`E(\lambda)` is the TOA spectral solar irradiance at a sun-earth
distance of one astronomical unit (AU).

Normalising with the equivalent band width gives the in-band solar irradiance:

.. math::

    E_{\lambda_{i}} = \frac{\int_0^\infty \Phi_{i}(\lambda) E(\lambda) \mathrm{d}\lambda} {\int_0^\infty \Phi_{i}(\lambda) \mathrm{d}\lambda}


In python code it may look like this:

   >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005, wavespace='wavenumber')
   >>> seviri = Seviri(wavespace='wavenumber')
   >>> rsr = {'wavenumber': seviri.rsr['VIS0.8']['wavenumber'], 'response': seviri.rsr['VIS0.8']['met8']}
   >>> print solar_irr.inband_solarflux(rsr)
   63767.9240506
   >>> print solar_irr.inband_solarirradiance(rsr)
   72.7869051247



Planck radiation
^^^^^^^^^^^^^^^^




