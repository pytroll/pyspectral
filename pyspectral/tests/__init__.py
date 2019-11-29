#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2019 Adam.Dybbroe

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

"""The tests package."""

import doctest
import os
from pyspectral import (blackbody,
                        near_infrared_reflectance,
                        solar)

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

TRAVIS = os.environ.get("TRAVIS", False)
APPVEYOR = os.environ.get("APPVEYOR", False)


def suite():
    """Perform the unit testing."""
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

    return mysuite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
