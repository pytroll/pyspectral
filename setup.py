#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013-2024 Pytroll
#
#
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

"""Setup for the Pyspectral package."""

import os.path

from setuptools import find_packages, setup

description = ('Reading and manipulaing satellite sensor spectral responses and the '
               'solar spectrum, to perfom various corrections to VIS and NIR band data')

with open('./README.md', 'r') as fd:
    long_description = fd.read()

requires = ['numpy', 'scipy>=1.6.0', 'python-geotiepoints>=1.1.1',
            'h5py>=2.5', 'requests', 'pyyaml', 'platformdirs']

dask_extra = ['dask[array]']
test_requires = ['pyyaml', 'dask[array]', 'xlrd', 'pytest', 'xarray', 'responses']

NAME = 'pyspectral'

setup(name=NAME,
      description=description,
      author='Adam Dybbroe',
      author_email='adam.dybbroe@smhi.se',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 ' +
                   'or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering'],
      url='https://github.com/pytroll/pyspectral',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='GPLv3',
      packages=find_packages(),
      include_package_data=True,
      package_data={
          # If any package contains *.txt files, include them:
          '': ['*.txt', '*.det'],
          'pyspectral': [os.path.join('etc', 'pyspectral.yaml'),
                         os.path.join('data', '*.dat'),
                         os.path.join('data', '*.XLS'),
                         'data/modis/terra/Reference_RSR_Dataset/*.det'],

      },

      # Project should use reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires=requires,
      extras_require={'xlrd': ['xlrd'], 'trollsift': ['trollsift'],
                      'matplotlib': ['matplotlib'],
                      'pandas': ['pandas'],
                      'tqdm': ['tqdm'],
                      'openpyxl': ['openpyxl'],
                      'test': test_requires,
                      'dask': dask_extra},
      scripts=['bin/plot_rsr.py', 'bin/composite_rsr_plot.py',
               'bin/download_atm_correction_luts.py',
               'bin/download_rsr.py'],
      data_files=[('share', ['pyspectral/data/e490_00a.dat',
                             'pyspectral/data/MSG_SEVIRI_Spectral_Response_Characterisation.XLS'])],
      python_requires='>=3.10',
      zip_safe=False,
      )
