#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2018 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The tests package"""

from pyspectral import (blackbody,
                        near_infrared_reflectance,
                        solar)

from pyspectral.tests import (test_rayleigh,
                              test_blackbody,
                              test_reflectance,
                              test_solarflux,
                              test_utils,
                              test_rad_tb_conversions,
                              test_rsr_reader,
                              test_atm_correction_ir)

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import doctest
import os
TRAVIS = os.environ.get("TRAVIS", False)
APPVEYOR = os.environ.get("APPVEYOR", False)


def suite():
    """The global test suite.
    """
    mysuite = unittest.TestSuite()
    if not TRAVIS and not APPVEYOR:
        # Test sphinx documentation pages:
        mysuite.addTests(doctest.DocFileSuite('../../doc/usage.rst'))
        mysuite.addTests(doctest.DocFileSuite('../../doc/rad_definitions.rst'))
        # mysuite.addTests(doctest.DocFileSuite('../../doc/seviri_example.rst'))
        mysuite.addTests(doctest.DocFileSuite('../../doc/37_reflectance.rst'))
        # Test the documentation strings
        mysuite.addTests(doctest.DocTestSuite(solar))
        mysuite.addTests(doctest.DocTestSuite(near_infrared_reflectance))
        mysuite.addTests(doctest.DocTestSuite(blackbody))

    # Use the unittests also
    mysuite.addTests(test_blackbody.suite())
    mysuite.addTests(test_rad_tb_conversions.suite())
    mysuite.addTests(test_solarflux.suite())
    mysuite.addTests(test_reflectance.suite())
    mysuite.addTests(test_utils.suite())
    mysuite.addTests(test_rayleigh.suite())
    mysuite.addTests(test_rsr_reader.suite())
    return mysuite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
