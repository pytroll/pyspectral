#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014, 2015, 2016 Adam Dybbroe

# Author(s):

#   Adam Dybbroe <adam.dybbroe@smhi.se>

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


try:
    with open('./README', 'r') as fd:
        long_description = fd.read()
except IOError:
    long_description = ''


from setuptools import setup
import imp

version = imp.load_source('pyspectral.version', 'pyspectral/version.py')

setup(name='pyspectral',
      version=version.__version__,
      description='Getting satellite sensor rsr functions and the solar spectrum',
      author='Adam Dybbroe',
      author_email='adam.dybbroe@smhi.se',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 ' +
                   'or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering'],
      url='https://github.com/adybbroe/pyspectral',
      # download_url="https://github.com/adybbroe/py....
      long_description=long_description,
      license='GPLv3',

      packages=['pyspectral'],

      include_package_data=True,
      package_data={
          # If any package contains *.txt files, include them:
          '': ['*.txt', '*.det'],
          'pyspectral': ['data/*.dat',
                         'data/*.XLS',
                         'data/modis/terra/Reference_RSR_Dataset/*.det'],
      },

      # Project should use reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires=['docutils>=0.3',
                        'numpy>=1.5.1', 'scipy>=0.8.1',
                        'h5py>=2.5',
                        'requests', 'tqdm'],
      #                  'requests>=2.7.0', 'tqdm>=4.8.4'],
      extras_require={'xlrd': ['xlrd'], 'matplotlib': ['matplotlib']},
      scripts=[],
      data_files=[('etc', ['etc/pyspectral.cfg']),
                  ('share', ['pyspectral/data/e490_00a.dat',
                             'pyspectral/data/MSG_SEVIRI_Spectral_Response_Characterisation.XLS'])],
      test_suite='pyspectral.tests.suite',
      tests_require=['mock', 'xlrd'],
      zip_safe=False
      )
