Pyspectral
==========


[![Build status](https://github.com/pytroll/pyspectral/workflows/CI/badge.svg?branch=main)](https://github.com/pytroll/pyspectral/workflows/CI/badge.svg?branch=main)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyspectral/badges/version.svg)](https://anaconda.org/conda-forge/pyspectral)
[![Build status](https://ci.appveyor.com/api/projects/status/5lm42n0l65l5o9xn?svg=true)](https://ci.appveyor.com/project/pytroll/pyspectral)
[![Coverage Status](https://coveralls.io/repos/github/pytroll/pyspectral/badge.svg?branch=main)](https://coveralls.io/github/pytroll/pyspectral?branch=main)
[![PyPI version](https://badge.fury.io/py/pyspectral.svg)](https://badge.fury.io/py/pyspectral)

Given a passive sensor on a meteorological satellite Pyspectral provides the
relative spectral response (rsr) function(s) and offer you some basic
operations like convolution with the solar spectrum to derive the in band solar
flux, for instance. The focus is on imaging sensors like AVHRR, VIIRS, MODIS, ABI,
AHI, OLCI and SEVIRI. But more sensors are included and if others are needed they can
be easily added. With Pyspectral it is possible to derive the reflective and
emissive parts of the signal observed in any NIR band around 3-4 microns where
both passive terrestrial emission and solar backscatter mix the information
received by the satellite. Furthermore Pyspectral allows correcting true color
imagery for the background (climatological) atmospheric signal due to Rayleigh
scattering of molecules, absorption by atmospheric gases and aerosols, and Mie
scattering of aerosols.

Adam Dybbroe
May 2021, Norrkoping, Sweden
