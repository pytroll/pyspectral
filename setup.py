"""Setup for the Pyspectral package."""

import os.path

from setuptools import find_packages, setup

description = ('Reading and manipulaing satellite sensor spectral responses and the '
               'solar spectrum, to perfom various corrections to VIS and NIR band data')

with open('./README.md', 'r') as fd:
    long_description = fd.read()

requires = ['numpy>=1.21', 'scipy>=1.6.0', 'python-geotiepoints>=1.1.1',
            'h5py>=2.5', 'requests', 'pyyaml', 'platformdirs']

dask_extra = ['dask[array]']
test_requires = ['pyyaml', 'dask[array]', 'xlrd', 'pytest>=9', 'xarray', 'responses']

NAME = 'pyspectral'

setup(name=NAME,
      description=description,
      author='Adam Dybbroe',
      author_email='adam.dybbroe@smhi.se',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering'],
      url='https://github.com/pytroll/pyspectral',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='Apache-2.0',
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
