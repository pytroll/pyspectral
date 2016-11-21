Rayleigh scattering correction
------------------------------

In particular at the shorter wavelengths around :math:`400-600 nm`, which
include the region used e.g. for ocean color products or true color imagery,
the Rayleigh scattering due to atmospheric molecules or atoms becomes
significant. As this atmospheric scattering is obscuring the retrieval of
surface parameters and since it is strongly dependent on observation geometry,
it is custom to try to correct or subtract this unwanted signal from the data
before performing the geophysical retrieval.

In order to correct for the Rayleigh scattering we have simulated the solar
reflectance under various sun-satellite viewing conditions for a set of
different standard atmospheres, using a radiative transfer model. For a given
atmosphere the reflectance is dependent on wavelenght, solar-zenith angle,
satellite zenith angle, and the relative sun-satellite azimuth difference
angle:

.. math::

    \sigma = \sigma({\theta}_0, \theta, \phi, \lambda)


To apply the rayleigh correction for a given satellite sensor band, the
procedure involves the following three steps:

 * Find the effective wavelength of the band
 * Derive the Rayleigh scattering part
 * Subtract that from the observations

As the Rayleigh scattering is proportional to :math:`\frac{1}{{\lambda}^4}` the
effective wavelength is derived by convolving the spectral response with
:math:`\frac{1}{{\lambda}^4}`. 

To get the Rayleigh scattering contribution for the VIIRS M2 band which should
be subtracted from the data the interface looks like this:

  >>> from pyspectral.rayleigh import Rayleigh
  >>> viirs = Rayleigh('Suomi-NPP', 'viirs')
  >>> refl_cor_m2 = viirs.get_reflectance(sunz, satz, ssadiff, 'M2') * 100.0


A few words on the Rayleigh scattering simulations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. image:: _static/refl_subarctic_winter_lambda_0400_ssa_000.png

  .. image:: _static/refl_subarctic_winter_lambda_0400_ssa_180.png

  .. image:: _static/refl_subarctic_winter_lambda_0500_ssa_090.png

  .. image:: _static/refl_subarctic_winter_lambda_0500_ssa_180.png
