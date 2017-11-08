pyspectral
==========

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9f039d7d640846ca89be8a78fa11e1f6)](https://www.codacy.com/app/adybbroe/pyspectral?utm_source=github.com&utm_medium=referral&utm_content=pytroll/pyspectral&utm_campaign=badger)
[![Build Status](https://travis-ci.org/pytroll/pyspectral.png?branch=pre-master)](https://travis-ci.org/pytroll/pyspectral)
[![Coverage Status](https://coveralls.io/repos/github/pytroll/pyspectral/badge.svg?branch=pre-master)](https://coveralls.io/github/pytroll/pyspectral?branch=pre-master)
[![Code Health](https://landscape.io/github/pytroll/pyspectral/pre-master/landscape.png)](https://landscape.io/github/pytroll/pyspectral/pre-master)
[![PyPI version](https://badge.fury.io/py/pyspectral.svg)](https://badge.fury.io/py/pyspectral)
[![Research software impact](http://depsy.org/api/package/pypi/pyspectral/badge.svg)](http://depsy.org/package/python/pyspectral)
[![Code Climate](https://codeclimate.com/github/pytroll/pyspectral/badges/gpa.svg)](https://codeclimate.com/github/pytroll/pyspectral)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/pytroll/pyspectral/badges/quality-score.png?b=develop)](https://scrutinizer-ci.com/g/pytroll/pyspectral/?branch=develop)


Given a passive sensor on a meteorological satellite the purpose of pyspectral
is to provide you with the relative spectral response (rsr) function(s) and
offer you some basic operations like convolution with the solar spectrum to
derive the in band solar flux for instance. The focus are imaging sensors like
AVHRR, VIIRS, MODIS, and SEVIRI. But more sensors are included and if other
sensors are needed they can easily be added. Pyspectral also allows correcting
true color imagery for rayleigh scattering (and background aerosol absorption).


Adam Dybbroe
November 2016, Norrkoping, Sweden
