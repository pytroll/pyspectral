Convert from original RSR data to pyspectral hdf5 format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The python modules in the directory ``rsr_convert_scripts`` contain code to convert
from the original agency specific relative spectral responses to the internal
unified pyspectral format in HDF5.

This conversion should normally never be done by the user. It will only be
relevant if the original responses are updated. It that case we will need to
redo the conversion and include the updated hdf5 file in the package data on
zenodo.org.

Running the conversion scripts requires the pyspectral.yaml file to point to
the directory of the original spectral response data. For AVHRR/3 onboard
Metop-C this may look like this:

.. code-block:: ini
                
   Metop-C-avhrr/3:
     path: /home/a000680/data/SpectralResponses/avhrr
     ch1: Metop_C_A309C001.txt
     ch2: Metop_C_A309C002.txt
     ch3a: Metop_C_A309C03A.txt
     ch3b: Metop_C_A309C03B.txt
     ch4: Metop_C_A309C004.txt
     ch5: Metop_C_A309C005.txt

     
Here <path> points to the place with the response functions for each
channel. For Metop-C, the case was a bit special, as we got one file with all
bands and using wavenumber and not wavelength. Therefore we first converted the
file using script "split_metop_avhrr_rsrfile.py".

For all the other sensors supported in Pyspectral we run the conversion script
directly on the files downloaded from internet (or acquired via mail-contact).


Conversion scripts
^^^^^^^^^^^^^^^^^^

.. code::

   %> aatsr_reader.py

Converting the original ENVISAT AATSR responses. The data are stored i MS Excel
format and the file name look like this: ``consolidatedsrfs.xls``

.. code::
   
   %> python abi_rsr.py

Converting from original GOES-16&17 ABI responses. The file names look like this: ``GOES-R_ABI_PFM_SRF_CWG_ch1.txt``


.. code::
   
   %> python ahi_rsr.py

Converting the original Himawari-8&9 AHI spectral responses. The data are stored i MS Excel
format and the file names look like this: ``AHI-9_SpectralResponsivity_Data.xlsx``


.. code::
   
   %> python avhrr_rsr.py

Converting from original Metop/NOAA AVHRR responses. The file names look like this: ``NOAA_10_A101C004.txt``

As mentioned above for Metop-C we chopped up the single original file into band
specific files to be consistent with the other AVHRRs. The original file we got
from EUMETSAT: ``AVHRR_A309_METOPC_SRF_PRELIMINARY.TXT``

.. code::

   %> python convert_avhrr_old2star.py

Convert the NOAA 15 Spectral responses to new NOAA STAR format.

.. code::
   
   %> python mersi2_rsr.py

Converts the FY-3D MERSI-2 spectral responses. Original files acquired via
personal contact has names like this: ``FY3D_MERSI_SRF_CH01_Pub.txt``

.. code::

   %> python modis_rsr.py

Converting the Terra/Aqua MODIS spectral responses to hdf5.
Original Aqua MODIS files have names like this: ``01.amb.1pct.det``
Terra files have names like this: ``rsr.1.oobd.det``

.. code::

   %> python msi_reader.py

The original Sentinel-2 A&B MSI spectral responses. Filenames look like this
``S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.0.xlsx``
   
.. code::

   %> python olci_rsr.py

Converting the Sentinel 3A OLCI RSR data to hdf5. The original OLCI
responses comes in a single netCDF4 file: ``OLCISRFNetCDF.nc4``

.. code::

   %> python oli_reader.py

Conversion of the original Landsat-8 OLI data. File names look like this: ``Ball_BA_RSR.v1.1-1.xlsx``

.. code::

   %> python seviri_rsr.py

Converting the Meteosat (second generation) SEVIRI responses to hdf5. Original
filename: ``MSG_SEVIRI_Spectral_Response_Characterisation.XLS``

.. code::

   %> python slstr_rsr.py

Converting the Sentinel-3 SLSTR spectral responses to hdf5. Original responses
from ESA comes as a set of netCDF files. One file per band. Band 1:
``SLSTR_FM02_S1_20150122.nc``

.. code::

   %> python viirs_rsr.py

Converting the NOAA-20 and Suomi-NPP VIIRS original responses to hdf5. File names
follow 9 different naming conventions depending on the band, here as given in
the pyspectral.yaml file:

.. code-block:: ini

   section1:
     filename: J1_VIIRS_Detector_RSR_V2/J1_VIIRS_RSR_{bandname}_Detector_Fused_V2.txt
     bands: [M1, M2, M3, M4, M5, M6, M7]

   section2:
     filename: J1_VIIRS_Detector_RSR_V2/J1_VIIRS_RSR_{bandname}_Detector_Fused_V2.txt
     bands: [I1, I2]

   section3:
     filename: J1_VIIRS_V1_RSR_used_in_V2/J1_VIIRS_RSR_M8_Det_V1.txt
     bands: [M8]
    
   section4:
     filename: J1_VIIRS_Detector_RSR_V2.1/J1_VIIRS_RSR_M9_Det_V2.1.txt
     bands: [M9]
  
   section5:
     filename: J1_VIIRS_V1_RSR_used_in_V2/J1_VIIRS_RSR_{bandname}_Det_V1.txt
     bands: [M10, M11, M12, M14, M15]

   section6:
     filename: J1_VIIRS_Detector_RSR_V2/J1_VIIRS_RSR_M13_Det_V2.txt
     bands: [M13]

   section7:
     filename: J1_VIIRS_V1_RSR_used_in_V2/J1_VIIRS_RSR_M16A_Det_V1.txt
     bands: [M16]

   section8:
     filename: J1_VIIRS_V1_RSR_used_in_V2/J1_VIIRS_RSR_{bandname}_Det_V1.txt
     bands: [I3, I4, I5]

   section9:
     filename: J1_VIIRS_Detector_RSR_V2/J1_VIIRS_RSR_DNBLGS_Detector_Fused_V2S.txt
     bands: [DNB]


Adam Dybbroe
Sat Dec  1 17:39:48 2018

.. code::

    %> python virr_rsr.py

Converting the FY-3B or FY-3C VIRR spectral responses to HDF5. Original files
for FY-3B come as ``.prn`` text files for each channel (ex. ``ch1.prn``). For
FY-3C they come as ``.txt`` text files for channels 1, 2, 6, 7, 8, 9, and 10
only with names like ``FY3C_VIRR_CH01.txt``.

