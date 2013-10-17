Derivation of the 3.7 micron reflectance
----------------------------------------

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
needed. The usual candidate at hand is the 11 brightness temperature
(e.g. VIIRS I5 or M12), since most objects behave approximately as blackbodies
in this spectral interval.

The :math:`3.7\mu m` channel reflectance may then be written as

.. math::

    \rho_{3.7} = \frac{L_{3.7} - \epsilon_{3.7} \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda } {\frac{1}{\pi} \mu_0 F_{3.7, 0}}

where :math:`L_{3.7}` is the measured radiance at :math:`3.7\mu m`, 
:math:`\Phi_{3.7} (\lambda)` is the :math:`L_{3.7}` channel
spectral response function, :math:`B_{\lambda}` is the Planck radiation, 
and :math:`T_{11}` is the :math:`11\mu m` channel brightness temperature.

If the observed object is optically thick (transmittance equals zero) then:

.. math::

    \epsilon_{3.7} = 1 - \rho_{3.7}

and then

.. math::

    \rho_{3.7} = \frac{L_{3.7} - \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda } {\frac{1}{\pi} \mu_0 F_{3.7, 0} - \int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{11}) \mathrm{d}\lambda }


Brightness temperature to radiance conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the satellite observation is given in terms of the brightness temperature,
then the corresponding radiance can be derived by convolving the relative
spectral response with the Planck function:

.. math::

    L_{3.7} = int_0^\infty \Phi_{3.7}(\lambda) B_{\lambda} (T_{3.7}) \mathrm{d}\lambda


Determination of the in-band solar flux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The solar flux (SI unit :math:`\frac{W}{m^2}`) over a spectral sensor band can
be derived by convolving the top of atmosphere spectral irradiance spectrum and
the sensor relative spectral response curve, so for the :math:`3.7\mu m` band
this would be:

.. math::

    F_{3.7} = int_0^\infty \Phi_{3.7}(\lambda) S(\lambda) \mathrm{d}\lambda 

where :math:`S(\lambda)` is the spectral solar irradiance.
