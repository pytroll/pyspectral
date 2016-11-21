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
  | :math:`\lambda`                 | Wavelength (:math:`\mu m`)                                                             |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\nu = \frac{1}{\lambda}` | Wavenumber (:math:`cm^{-1}`)                                                           |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\lambda_{c}`             | Central wavelength for a given band/channel (:math:`\mu m`)                            |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\nu_{c}`                 | Central wavelength for a given band/channel (:math:`cm^{-1}`)                          |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`\Phi_{i}(\lambda)`       | Relative spectral response for band :math:`i` as a function of wavelength              |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`E_{\lambda}`             | Spectral irradiance at wavelength :math:`\lambda` (:math:`W/m^2 \mu m^{-1}`)           |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`E_{\nu}`                 | Spectral irradiance at wavenumber :math:`\nu` (:math:`W/m^2 (cm^{-1})^{-1}`)           |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`B_{\lambda}`             | Blackbody radiation at wavelength :math:`\lambda` (:math:`W/m^2  \mu m^{-1}`)          |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`B_{\nu}`                 | Blackbody radiation at wavenumber :math:`\nu` (:math:`W/m^2 (cm^{-1})^{-1}`)           |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`L_{\nu}`                 | Spectral radiance at wavenumber :math:`\nu` (:math:`W/m^2 sr^{-1} (cm^{-1})^{-1}`)     |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`L_{\lambda}`             | Spectral radiance at wavelength :math:`\lambda` (:math:`W/m^2 sr^{-1} \mu m^{-1}`)     |
  +---------------------------------+----------------------------------------------------------------------------------------+


Constants
^^^^^^^^^

  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`k_B`                     | Boltzmann constant (:math:`1.3806488 1e−23`)                                           |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`h`                       | Planck constant (:math:`6.62606957 1e-34`)                                             |
  +---------------------------------+----------------------------------------------------------------------------------------+
  | :math:`c`                       | Speed of light in vacuum (:math:`2.99792458 1e8`)                                      |
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

Taking SEVIRI as an example, and looking at the visible channel on Meteosat-8,
we see that this is indeed true:

  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> from pyspectral.utils import convert2wavenumber, get_central_wave
  >>> seviri = RelativeSpectralResponse('Meteosat-8', 'seviri')
  >>> print get_central_wave(seviri.rsr['VIS0.6']['det-1']['wavelength'], seviri.rsr['VIS0.6']['det-1']['response'])
  0.640216
  >>> rsr, info = convert2wavenumber(seviri.rsr)
  >>> print info
  {'si_scale': 100.0, 'unit': 'cm-1'}
  >>> wvc = get_central_wave(rsr['VIS0.6']['det-1']['wavenumber'], rsr['VIS0.6']['det-1']['response'])
  >>> print wvc
  15682.6
  >>> print 1./wvc*1e4
  0.637648471994

This was using the pyspectral unified HDF5 formated spectral response data. If
you want to use the original spectral response data from EUMETSAT the code may
look like this:
 
  >>> from pyspectral.seviri_rsr import Seviri
  >>> seviri = Seviri()
  >>> print seviri.central_wavelength['VIS0.6']['Meteosat-8']
  0.640215597159
  >>> seviri = Seviri(wavespace='wavenumber')
  >>> print seviri.central_wavenumber['VIS0.6']['Meteosat-8']
  15682.623379
  >>> print 1./seviri.central_wavenumber['VIS0.6']['Meteosat-8']*1e4
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

    E_\nu = {E_\lambda \lambda^2 * 0.1}



TOA Solar irridiance and solar constant
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, the TOA solar irradiance in wavelength space:

  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005) 
  >>> print("%6.2f" % solar_irr.solar_constant())
  1366.09
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


In-band solar flux
^^^^^^^^^^^^^^^^^^

The solar flux (SI unit :math:`\frac{W}{m^2}`) over a spectral sensor band can
be derived by convolving the top of atmosphere solar spectral irradiance and
the sensor relative spectral response. For band :math:`i`:

.. math::

    F_i = \int_0^\infty \Phi_{i}(\lambda) E(\lambda) \mathrm{d}\lambda 

where :math:`E(\lambda)` is the TOA spectral solar irradiance at a sun-earth
distance of one astronomical unit (AU).

.. Normalising with the equivalent band width gives the in-band solar irradiance:

..     E_{\lambda_{i}} = \frac{\int_0^\infty \Phi_{i}(\lambda) E(\lambda) \mathrm{d}\lambda} {\int_0^\infty \Phi_{i}(\lambda) \mathrm{d}\lambda}


In python code it may look like this:

   >>> from pyspectral.rsr_reader import RelativeSpectralResponse
   >>> from pyspectral.utils import convert2wavenumber, get_central_wave
   >>> seviri = RelativeSpectralResponse('Meteosat-8', 'seviri')
   >>> rsr, info = convert2wavenumber(seviri.rsr)
   >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)

   >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.0005, wavespace='wavenumber')
   >>> print solar_irr.inband_solarflux(rsr['VIS0.8'])
   63767.9084048


Planck radiation
^^^^^^^^^^^^^^^^

Planck's law describes the electromagnetic radiation emitted by a black body in
thermal equilibrium at a definite temperature.

Thus for wavelength :math:`\lambda` the Planck radiation or Blackbody
radiation :math:`B({\lambda})` can be written as:

.. math::

   B_{\lambda}(T) = \frac{2hc^{2}}{{\lambda}^{5}} \frac{1} {e^{\frac{hc}{\lambda k_B T}} - 1}

and expressed as a function of wavenumber :math:`\nu`:

.. math::

   B_{\nu}(T) = 2hc^2{\nu}^3 \frac{1}{e^{\frac{h c \nu}{k_B T}} - 1}

In python it may look like this:

   >>> from pyspectral.blackbody import blackbody_wn
   >>> wavenumber = 90909.1
   >>> rad = blackbody_wn((wavenumber, ), [300., 301])
   >>> print rad
   [0.001158354413530655 0.0011754771652280277]

Which are the spectral radiances in SI units at wavenumber around :math:`909 cm^{-1}` at
temperatures 300 and 301 Kelvin. In units of :math:`mW/m^2 (cm^{-1})^{-1}\ sr^{-1}` this becomes:

   >>> print rad*1e+5
   [115.83544135306549 117.54771652280277]

And using wavelength representation:

   >>> from pyspectral.blackbody import blackbody
   >>> wvl = 1./wavenumber
   >>> rad = blackbody(wvl, [300., 301])
   >>> print rad
   [9573178.885963218 9714689.258871676]

Which are the spectral radiances in SI units around :math:`11 \mu m` at
temperatures 300 and 301 Kelvin. In units of :math:`mW/m^2\ m^{-1} sr^{-1}` this becomes:

   >>> print rad*1e-6
   [9.573178885963218 9.714689258871676]


The inverse Planck function
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inverting the Planck function allows to derive the brightness temperature given
the spectral radiance. Expressed in wavenumber space this becomes:

.. math::

   T_B = T(B_{\nu}) = \frac{hc\nu}{k_B} log^{-1}\{\frac{2hc^2{\nu}^3}{B_{\nu}} + 1\}

With the spectral radiance given as a function of wavelength the equation looks like this:

.. math::

   T_B = T(B_{\lambda}) = \frac{hc}{\lambda k_B} log^{-1}\{\frac{2hc^2}{B_{\lambda} {\lambda}^5} + 1\}


In python it may look like this:

   >>> from pyspectral.blackbody import blackbody_wn_rad2temp
   >>> wavenumber = 90909.1
   >>> temp = blackbody_wn_rad2temp(wavenumber, [0.001158354, 0.001175477])
   >>> print temp
   [ 299.99998562  301.00000518]


Provided the input is a central wavenumber or wavelength as defined above, this
gives the brightness temperature calculation under the assumption of a linear
planck function as a function of wavelength or wavenumber over the spectral
band width and provided a constant relative spectral response. To get a more
precise derivation of the brightness temperature given a measured radiance one
needs to convolve the inverse Planck function with the relative spectral
response function for the band in question:

.. math::

   T_B = \frac{\int_0^\infty \Phi_{i}(\lambda) T(B_{\lambda}) \mathrm{d}\lambda}
   {\int_0^\infty \Phi_{i}(\lambda) \mathrm{d}\lambda}

or

.. math::

   T_B = T(B_{\nu}) = \frac{\int_0^\infty \Phi_{i}(\nu) T(B_{\nu}) \mathrm{d}\nu}
   {\int_0^\infty \Phi_{i}(\nu) \mathrm{d}\nu}
