Satellite sensors supported
===========================

Below we list the satellite sensors for which the relative spectral responses
have been included in PySpectral. 

.. list-table:: Satellite sensors supported
    :header-rows: 1

    * - Satellite sensor
      - Filename
      - Link to the original RSR
    * - Meteosat-8 seviri
      - `rsr_seviri_Meteosat-8.h5`
      - GSICS_
    * - Meteosat-9 seviri
      - `rsr_seviri_Meteosat-9.h5`
      - GSICS_
    * - Meteosat-10 seviri
      - `rsr_seviri_Meteosat-10.h5`
      - GSICS_
    * - Meteosat-11 seviri
      - `rsr_seviri_Meteosat-11.h5`
      - GSICS_
    * - GOES-16 abi
      - `rsr_abi_GOES-16.h5`
      - GOES-R_
    * - Himawari-8 ahi
      - `rsr_ahi_Himawari-8.h5`
      - JMA_
    * - Himawari-9 ahi
      - `rsr_ahi_Himawari-9.h5`
      - JMA_
    * - GEO-KOMPSAT-2A ami
      - `rsr_ami_GEO-KOMPSAT-2A.h5`
      - NWPSAF-GeoKompsat-2A-ami_
    * - FY-4A agri
      - `rsr_agri_FY-4A.h5`
      - NSMC-fy4a_
    * - Envisat aatsr
      - `rsr_aatsr_Envisat.h5`
      - ESA-Envisat_
    * - TIROS-N to NOAA-19 avhrr
      - e.g. `rsr_avhrr3_NOAA-19.h5`
      - GSICS_
    * - Metop-A avhrr/3
      - `rsr_avhrr3_Metop-A.h5`
      - GSICS_
    * - Metop-B avhrr/3
      - `rsr_avhrr3_Metop-B.h5`
      - GSICS_
    * - Metop-C avhrr
      - `rsr_avhrr3_Metop-C.h5`
      - GSICS_ (Acquired via personal contact)
    * - EOS-Terra modis
      - `rsr_modis_EOS-Terra.h5`
      - GSICS_
    * - EOS-Aqua modis
      - `rsr_modis_EOS-Aqua.h5`
      - GSICS_
    * - Sentinel-3A slstr
      - `rsr_slstr_Sentinel-3A.h5`
      - ESA-Sentinel-SLSTR_
    * - Sentinel-3A olci
      - `rsr_olci_Sentinel-3A.h5`
      - ESA-Sentinel-OLCI_
    * - Sentinel-2A msi
      - `rsr_msi_Sentinel-2A.h5`
      - ESA-Sentinel-MSI_
    * - Sentinel-2B msi
      - `rsr_msi_Sentinel-2B.h5`
      - ESA-Sentinel-MSI_
    * - NOAA-20 viirs
      - `rsr_viirs_NOAA-20.h5`
      - NESDIS_
    * - Suomi-NPP viirs
      - `rsr_viirs_Suomi-NPP.h5`
      - GSICS_
    * - Landsat-8 oli
      - `rsr_oli_Landsat-8.h5`
      - NASA-Landsat-OLI_
    * - FY-3D mersi-2
      - `rsr_mersi-2_FY-3D.h5`
      - CMA_ (Acquired via personal contact)
    * - HY-1C cocts
      - `rsr_cocts_HY-1C.h5`
      - (Acquired via personal contact)
    * - Metop-SG-A1 MetImage
      - `rsr_metimage_Metop-SG-A1.h5`
      - NWPSAF-MetImage_

.. _Eumetsat: https://www.eumetsat.int/website/home/Data/Products/Calibration/MSGCalibration/index.html
.. _GSICS: https://www.star.nesdis.noaa.gov/smcd/GCC/instrInfo-srf.php
.. _GOES-R: http://ncc.nesdis.noaa.gov/GOESR/docs/GOES-R_ABI_PFM_SRF_CWG_v3.zip
.. _JMA: http://www.data.jma.go.jp/mscweb/en/himawari89/space_segment/spsg_ahi.html#srf
.. _ESA-Envisat: http://envisat.esa.int/handbooks/aatsr/aux-files/consolidatedsrfs.xls
.. _ESA-Sentinel-OLCI: https://sentinel.esa.int/documents/247904/322304/OLCI+SRF+%28NetCDF%29/15cfd7a6-b7bc-4051-87f8-c35d765ae43a
.. _ESA-Sentinel-SLSTR: https://sentinel.esa.int/documents/247904/322305/SLSTR_FM02_Spectral_Responses_Necdf_zip/3a4482b8-6e44-47f3-a8f2-79c000663976
.. _ESA-Sentinel-MSI: https://earth.esa.int/documents/247904/685211/S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.0.xlsx
.. _NASA-Landsat-OLI: https://landsat.gsfc.nasa.gov/wp-content/uploads/2013/06/Ball_BA_RSR.v1.1-1.xlsx
.. _NESDIS: https://ncc.nesdis.noaa.gov/J1VIIRS/J1VIIRSSpectralResponseFunctions.php
.. _CMA: http://www.cma.gov.cn/en2014/
.. _NWPSAF-MetImage: https://nwpsaf.eu/downloads/rtcoef_rttov12/ir_srf/rtcoef_metopsg_1_metimage_srf.html
.. _NWPSAF-GeoKompsat-2A-ami: https://nwpsaf.eu/downloads/rtcoef_rttov12/ir_srf/rtcoef_gkompsat2_1_ami_srf.html
.. _NSMC-fy4a: http://fy4.nsmc.org.cn/portal/cn/fycv/srf.html
