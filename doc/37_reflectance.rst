Derivation of the 3.7 micron reflectance
----------------------------------------

It is well known that the top of atmosphere signal (observed radiance or
brightness temperature) of a sensor band in the near infrared part of the
spectrum between around :math:`3-4 \mu m` is composed of a thermal (or
emissive) part and a part stemming from reflection of incoming sunlight.

With some assumptions it is possible to separate the two and derive a solar
reflectance in the band from the observed brightness temperature. Below we will
demonstrate the theory on how this separation is done. But, first we need to
demonstrate how the spectral radiance can be calculated from an observed
brightness temperature, knowing the relative spectral response of the the
sensor band.


Brightness temperature to spectral radiance 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the satellite observation is given in terms of the brightness temperature,
then the corresponding spectral radiance can be derived by convolving the relative
spectral response with the Planck function and divding by the equivalent band width:

.. math::
    L_{3.7} = \frac{\int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{3.7}) \mathrm{d}\lambda}{\widetilde{\Delta \lambda}}
    :label: spectral_radiance
            
where the equivalent band width :math:`\widetilde{\Delta \lambda}` is defined as:

.. math::

    \widetilde{\Delta \lambda} = \int_0^\infty \Phi_{3.7}(\lambda) \mathrm{d}\lambda

:math:`L_{3.7}` is the measured radiance at :math:`3.7\mu m`, 
:math:`\Phi_{3.7} (\lambda)` is the :math:`3.7 \mu m` channel
spectral response function, and :math:`B_{\lambda}` is the Planck radiation.

    
This gives the spectral radiance given the brightness temperature and may be
expressed in :math:`W/m^2 sr^{-1} \mu m^{-1}`, or using SI units :math:`W/m^2 sr^{-1} m^{-1}`.

  >>> from pyspectral.radiance_tb_conversion import RadTbConverter
  >>> import numpy as np
  >>> sunz = np.array([68.98597217,  68.9865146 ,  68.98705756,  68.98760105, 68.98814508])
  >>> tb37 = np.array([298.07385254, 297.15478516, 294.43276978, 281.67633057, 273.7923584])
  >>> viirs = RadTbConverter('Suomi-NPP', 'viirs', 'M12')
  >>> rad37 = viirs.tb2radiance(tb37)
  >>> print([np.round(rad, 7) for rad in rad37['radiance']])
  [369717.4972296, 355110.6414922, 314684.3507084, 173143.4836477, 116408.0022674]
  >>> rad37['unit']
  'W/m^2 sr^-1 m^-1'

  
In order to get the total radiance over the band one has to multiply with the equivalent band width.

  >>> from pyspectral.radiance_tb_conversion import RadTbConverter
  >>> import numpy as np
  >>> tb37 = np.array([298.07385254, 297.15478516, 294.43276978, 281.67633057, 273.7923584])
  >>> viirs = RadTbConverter('Suomi-NPP', 'viirs', 'M12')
  >>> rad37 = viirs.tb2radiance(tb37, normalized=False)
  >>> print([np.round(rad, 8) for rad in rad37['radiance']])
  [0.07037968, 0.06759911, 0.05990353, 0.03295971, 0.02215951]
  >>> rad37['unit']
  'W/m^2 sr^-1'

By passing ``normalized=False`` to the method the division by the equivalent
band width is omitted. The equivalent width is provided as an attribute in SI
units (:math:`m`):

  >>> from pyspectral.radiance_tb_conversion import RadTbConverter
  >>> viirs = RadTbConverter('Suomi-NPP', 'viirs', 'M12')
  >>> viirs.rsr_integral
  1.903607e-07


Inserting the Planck radiation:

.. math::
    L_{3.7} = \frac{2hc^{2} \int_0^\infty \frac{\Phi_{3.7}(\lambda)}{{\lambda}^{5}} \frac{\mathrm{d}\lambda} {e^{\frac{hc}{\lambda k_B(T_{3.7})}} - 1}}{\widetilde{\Delta \lambda}}
    :label: full_spectral_radiance

The total band integrated spectral radiance or the in band radiance is then:

.. math::
    L_{3.7} = 2hc^{2} \int_0^\infty \frac{\Phi_{3.7}(\lambda)}{{\lambda}^{5}} \frac{\mathrm{d}\lambda} {e^{\frac{hc}{\lambda k_B(T_{3.7})}} - 1}
    :label: inband_radiance

            
This is expressed in wavelength space. But the spectral radiance can also be
given in terms of the wavenumber :math:`\nu`, provided the relative spectral
response is given as a function of :math:`\nu`:

.. math::

    L_{{\nu}(3.7)} = \frac{\int_0^\infty \Phi_{3.7}(\nu) B_{\nu} (T_{3.7}) \mathrm{d}\nu}{\widetilde{\Delta \nu}}

where the equivalent band width :math:`\widetilde{\Delta \nu}` is defined as:

.. math::

    \widetilde{\Delta \nu} = \int_0^\infty \Phi_{3.7}(\nu) \mathrm{d}\nu

and inserting the Planck radiation:

.. math::

    L_{{\nu}(3.7)} = \frac{\frac{2h}{c^2} \int_0^\infty \Phi_{3.7}(\nu) \frac{{\nu}^3 \mathrm{d}\nu}{e^{\frac{h c}{\lambda k_B T:{3.7}}} - 1} }{\widetilde{\Delta \nu}}



Determination of the in-band solar flux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The solar flux (SI unit :math:`\frac{W}{m^2}`) over a spectral sensor band can
be derived by convolving the top of atmosphere spectral irradiance and the
sensor relative spectral response curve, so for the :math:`3.7\mu m` band this
would be:

.. math::
    F_{3.7} = \int_0^\infty \Phi_{3.7}(\lambda) S(\lambda) \mathrm{d}\lambda 
    :label: solarflux

where :math:`S(\lambda)` is the spectral solar irradiance.

  >>> from pyspectral.rsr_reader import RelativeSpectralResponse
  >>> from pyspectral.solar import (SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
  >>> viirs = RelativeSpectralResponse('Suomi-NPP', 'viirs')
  >>> solar_irr = SolarIrradianceSpectrum(TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.005)
  >>> sflux = solar_irr.inband_solarflux(viirs.rsr['M12'])
  >>> print(np.round(sflux, 7))
  2.2428119

Derive the reflective part of the observed 3.7 micron radiance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The monochromatic reflectivity (or reflectance) :math:`\rho_{\lambda}` is the
ratio of the reflected (backscattered) radiance to the incident radiance. In
the case of solar reflection one can write:

.. math::

    \rho_{\lambda} = \frac{L_{\lambda}}{\mu_0 L_{\lambda 0}}

where :math:`L_{\lambda}` is the measured radiance, :math:`L_{\lambda 0}` is
the incoming solar radiance, and :math:`\mu_0` is the cosine of the solar
zenith angle :math:`\theta_0`.


Assuming the solar radiance is independent of direction, the equation for the
reflectance can be written in terms of the solar flux :math:`F_{\lambda 0}`:

.. math::

    \rho_{\lambda} = \frac{L_{\lambda}}{\frac{1}{\pi} \mu_0 F_{\lambda 0}}

For the :math:`3.7\mu m` channel the outgoing radiance is due to solar
reflection and thermal emission. Thus in order to determine a :math:`3.7\mu m`
channel reflectance, it is necessary to subtract the thermal part from the
satellite signal. To do this, the temperature of the observed object is
needed. The usual candidate at hand is the :math:`11 \mu m` brightness temperature
(e.g. VIIRS I5 or M12), since most objects behave approximately as blackbodies
in this spectral interval.

The :math:`3.7\mu m` channel reflectance may then be written as (we now operate
with the in band radiance given by :eq:`inband_radiance`)

.. math::

    \rho_{3.7} = \frac{L_{3.7} - \epsilon_{3.7} \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda } {\frac{1}{\pi} \mu_0 F_{3.7, 0}}

where :math:`L_{3.7}` is the measured radiance at :math:`3.7\mu m`, 
:math:`\Phi_{3.7} (\lambda)` is the :math:`3.7 \mu m` channel
spectral response function, :math:`B_{\lambda}` is the Planck radiation, 
and :math:`T_{11}` is the :math:`11\mu m` channel brightness temperature.
Observe that :math:`L_{3.7}` is now the radiance provided by :eq:`inband_radiance`.


If the observed object is optically thick (transmittance equals zero) then:

.. math::

    \epsilon_{3.7} = 1 - \rho_{3.7}

and then, with the radiance :math:`L_{3.7}` derived using
:eq:`full_spectral_radiance` and the solar flux given by :eq:`solarflux` we get:

.. math::
    \rho_{3.7} = \frac{L_{3.7} - \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda } {\frac{1}{\pi} \mu_0 F_{3.7, 0} - \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda }
   :label: refl37
           
In Python this becomes:

  >>> from pyspectral.near_infrared_reflectance import Calculator
  >>> import numpy as np
  >>> refl_m12 = Calculator('Suomi-NPP', 'viirs', 'M12')
  >>> sunz = np.array([68.98597217,  68.9865146 ,  68.98705756,  68.98760105, 68.98814508])
  >>> tb37 = np.array([298.07385254, 297.15478516, 294.43276978, 281.67633057, 273.7923584])
  >>> tb11 = np.array([271.38806152, 271.38806152, 271.33453369, 271.98553467, 271.93609619])
  >>> m12r = refl_m12.reflectance_from_tbs(sunz, tb37, tb11)
  >>> print(np.any(np.isnan(m12r)))
  False
  >>> print([np.round(refl, 6) for refl in m12r])
  [0.214329, 0.202852, 0.17064, 0.054089, 0.008381]

We can try decompose equation :eq:`refl37` above using the example of VIIRS M12 band:


  >>> from pyspectral.radiance_tb_conversion import RadTbConverter
  >>> import numpy as np
  >>> sunz = np.array([68.98597217,  68.9865146 ,  68.98705756,  68.98760105, 68.98814508])
  >>> tb37 = np.array([298.07385254, 297.15478516, 294.43276978, 281.67633057, 273.7923584])
  >>> tb11 = np.array([271.38806152, 271.38806152, 271.33453369, 271.98553467, 271.93609619])
  >>> viirs = RadTbConverter('Suomi-NPP', 'viirs', 'M12')
  >>> rad37 = viirs.tb2radiance(tb37, normalized=False)
  >>> rad11 = viirs.tb2radiance(tb11, normalized=False)
  >>> sflux = 2.242817881698326
  >>> nomin = rad37['radiance'] - rad11['radiance']
  >>> print(np.isnan(nomin))
  [False False False False False]
  >>> print([np.round(val, 8) for val in nomin])
  [0.05083677, 0.0480562, 0.04041571, 0.01279277, 0.00204485]
  >>> denom = np.cos(np.deg2rad(sunz))/np.pi * sflux - rad11['radiance']
  >>> print(np.isnan(denom))
  [False False False False False]
  >>> print([np.round(val, 8) for val in denom])
  [0.23646312, 0.23645681, 0.23650559, 0.23582014, 0.23586609]
  >>> res = nomin/denom
  >>> print(np.isnan(res))
  [False False False False False]
  >>> print([np.round(val, 8) for val in res])
  [0.21498817, 0.20323458, 0.17088693, 0.05424801, 0.00866952]


Derive the emissive part of the 3.7 micron band
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we have the reflective part of the :math:`3.x` signal, it is easy to derive
the emissive part, under the same assumptions of completely opaque (zero
transmissivity) objects. 

.. math::

   L_{3.7, thermal} = (1 - \rho_{3.7}) \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda

Using the example of the VIIRS M12 band from above this gives the following spectral radiance:

  >>> from pyspectral.near_infrared_reflectance import Calculator
  >>> import numpy as np
  >>> refl_m12 = Calculator('Suomi-NPP', 'viirs', 'M12')
  >>> sunz = np.array([68.98597217,  68.9865146 ,  68.98705756,  68.98760105, 68.98814508])
  >>> tb37 = np.array([298.07385254, 297.15478516, 294.43276978, 281.67633057, 273.7923584])
  >>> tb11 = np.array([271.38806152, 271.38806152, 271.33453369, 271.98553467, 271.93609619])
  >>> m12r = refl_m12.reflectance_from_tbs(sunz, tb37, tb11)
  >>> tb = refl_m12.emissive_part_3x()
  >>> ['{tb:6.3f}'.format(tb=np.round(t, 4)) for t in tb]
  ['266.996', '267.262', '267.991', '271.033', '271.927']
  >>> rad = refl_m12.emissive_part_3x(tb=False)
  >>> ['{rad:6.1f}'.format(rad=np.round(r, 1)) for r in rad.compute()]
  ['80285.2', '81458.0', '84749.7', '99761.4', '104582.0']

