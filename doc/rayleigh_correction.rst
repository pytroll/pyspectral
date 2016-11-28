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

To get the Rayleigh scattering contribution for an arbitrary band, first the
solar zenith, satellite zenith and the sun-satellite azimuth difference angles
should be loaded.

For the VIIRS M2 band the interface looks like this:

  >>> from pyspectral.rayleigh import Rayleigh
  >>> viirs = Rayleigh('Suomi-NPP', 'viirs')
  >>> refl_cor_m2 = viirs.get_reflectance(sunz, satz, ssadiff, 'M2')

This rayleigh contribution should then of course be subtracted from the
data. Optionally the blueband can be provided as the fifth argument, which will
provide a more gentle scaling in cases of high reflectances (above 20%):

  >>> refl_cor_m2 = viirs.get_reflectance(sunz, satz, ssadiff, 'M2', blueband)

In case you do not know the name of the band (defined in the pyspectral rsr files) you can provide the approximate band frequency in micro meters:

  >>> refl_cor_m2 = viirs.get_reflectance(sunz, satz, ssadiff, 0.45, blueband)

At the moment we have done simulations for a set of standard atmospheres in two
different configuration, one only considering rayleigh scattering, and one also
accounting for aerosols. On default we use the simulations without aerosol
absorption, but it is possible to specify if you want the other setup, e.g.:

  >>> from pyspectral.rayleigh import Rayleigh
  >>> viirs = Rayleigh('Suomi-NPP', 'viirs', atmosphere='midlatitude summer', rural_aerosol=True)
  >>> refl_cor_m2 = viirs.get_reflectance(sunz, satz, ssadiff, 0.45, blueband)


A few words on the Rayleigh scattering simulations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. image:: _static/refl_subarctic_winter_lambda_0400_ssa_000.png

  .. image:: _static/refl_subarctic_winter_lambda_0400_ssa_180.png

  .. image:: _static/refl_subarctic_winter_lambda_0500_ssa_090.png

  .. image:: _static/refl_subarctic_winter_lambda_0500_ssa_180.png
