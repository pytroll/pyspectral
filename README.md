pyspectral
==========

[![Build Status](https://travis-ci.org/pytroll/pyspectral.png?branch=pre-master)](https://travis-ci.org/pytroll/pyspectral)
[![Coverage Status](https://coveralls.io/repos/github/pytroll/pyspectral/badge.svg?branch=pre-master)](https://coveralls.io/github/pytroll/pyspectral?branch=pre-master)
[![Code Health](https://landscape.io/github/pytroll/pyspectral/pre-master/landscape.png)](https://landscape.io/github/pytroll/pyspectral/pre-master)
[![PyPI version](https://badge.fury.io/py/pyspectral.svg)](https://badge.fury.io/py/pyspectral)
[![Research software impact](http://depsy.org/api/package/pypi/pyspectral/badge.svg)](http://depsy.org/package/python/pyspectral)


Given a passive sensor on a meteorological satellite the purpose of pyspectral
is to provide you with the relative spectral response (rsr) function(s) and
offer you some basic operations like convolution with the solar spectrum to
derive the in band solar flux for instance. The focus are imaging sensors like
AVHRR, VIIRS, MODIS, and SEVIRI. But more sensors are included and if other
sensors are needed they can easily be added. Pyspectral also allows correcting
true color imagery for rayleigh scattering (and background aerosol absorption).


Adam Dybbroe
November 2016, Norrkoping, Sweden
