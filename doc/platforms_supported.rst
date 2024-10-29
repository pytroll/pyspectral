Satellite sensors supported
===========================

Below we list the satellite sensors for which the relative spectral responses
have been included in Pyspectral.

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
    * - GOES-17 abi
      - `rsr_abi_GOES-17.h5`
      - GOES-S_
    * - GOES-18 abi
      - `rsr_abi_GOES-18.h5`
      - GOES-T_
    * - GOES-19 abi
      - `rsr_abi_GOES-19.h5`
      - GOES-U_
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
    * - Sentinel-3B slstr
      - `rsr_slstr_Sentinel-3B.h5`
      - ESA-Sentinel-SLSTR_
    * - Sentinel-3A olci
      - `rsr_olci_Sentinel-3A.h5`
      - ESA-Sentinel-OLCI_
    * - Sentinel-3B olci
      - `rsr_olci_Sentinel-3B.h5`
      - ESA-Sentinel-OLCI_
    * - Sentinel-2A msi
      - `rsr_msi_Sentinel-2A.h5`
      - ESA-Sentinel-MSI_
    * - Sentinel-2B msi
      - `rsr_msi_Sentinel-2B.h5`
      - ESA-Sentinel-MSI_
    * - Sentinel-2C msi
      - `rsr_msi_Sentinel-2C.h5`
      - ESA-Sentinel-MSI_
    * - NOAA-20 viirs
      - `rsr_viirs_NOAA-20.h5`
      - NESDIS_
    * - Suomi-NPP viirs
      - `rsr_viirs_Suomi-NPP.h5`
      - GSICS_
    * - Landsat-8 oli
      - `rsr_oli_tirs_Landsat-8.h5`
      - NASA-Landsat-8-OLI_
    * - Landsat-8 tirs
      - `rsr_oli_tirs_Landsat-8.h5`
      - NASA-Landsat-8-TIRS_
    * - Landsat-9 oli-2
      - `rsr_oli_tirs_Landsat-9.h5`
      - NASA-Landsat-9-OLI_
    * - Landsat-9 tirs-2
      - `rsr_oli_tirs_Landsat-9.h5`
      - NASA-Landsat-9-TIRS_
    * - FY-3D mersi-2
      - `rsr_mersi-2_FY-3D.h5`
      - CMA_ (Acquired via personal contact)
    * - HY-1C cocts
      - `rsr_cocts_HY-1C.h5`
      - (Acquired via personal contact)
    * - Metop-SG-A1 MetImage
      - `rsr_metimage_Metop-SG-A1.h5`
      - NWPSAF-MetImage_
    * - Meteosat-12 fci
      - `rsr_fci_Meteosat-12.h5`
      - NWPSAF-Meteosat-12-fci_
    * - MTG-I1 fci (NB! Identical to Meteosat-12 fci)
      - `rsr_fci_MTG-I1.h5`
      - NWPSAF-Meteosat-12-fci_


.. _Eumetsat: https://www.eumetsat.int/website/home/Data/Products/Calibration/MSGCalibration/index.html
.. _GSICS: https://www.star.nesdis.noaa.gov/smcd/GCC/instrInfo-srf.php
.. _GOES-R: https://ncc.nesdis.noaa.gov/GOESR/docs/GOES-R_ABI_PFM_SRF_CWG_v3.zip
.. _GOES-S:  https://ncc.nesdis.noaa.gov/GOESR/docs/GOES-R_ABI_FM2_SRF_CWG.zip
.. _GOES-T:  https://ncc.nesdis.noaa.gov/GOESR/docs/GOES-R_ABI_FM3_SRF_CWG.zip
.. _GOES-U:  https://ncc.nesdis.noaa.gov/GOESR/docs/GOES-R_ABI_FM4_SRF_CWG.zip
.. _JMA: http://www.data.jma.go.jp/mscweb/en/himawari89/space_segment/spsg_ahi.html#srf
.. _ESA-Envisat: http://envisat.esa.int/handbooks/aatsr/aux-files/consolidatedsrfs.xls
.. _ESA-Sentinel-OLCI: https://sentinel.esa.int/documents/247904/322304/OLCI+SRF+%28NetCDF%29/15cfd7a6-b7bc-4051-87f8-c35d765ae43a
.. _ESA-Sentinel-SLSTR: https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-3-slstr/instrument/measured-spectral-response-function-data
.. _ESA-Sentinel-MSI: https://earth.esa.int/documents/247904/685211/S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.0.xlsx
.. _NASA-Landsat-8-OLI: https://landsat.gsfc.nasa.gov/wp-content/uploads/2014/09/Ball_BA_RSR.v1.2.xlsx
.. _NASA-Landsat-9-OLI: https://landsat.gsfc.nasa.gov/wp-content/uploads/2024/03/L9_OLI2_Ball_BA_RSR.v2-1.xlsx
.. _NASA-Landsat-8-TIRS: https://landsat.gsfc.nasa.gov/wp-content/uploads/2013/06/TIRS_Relative_Spectral_Responses.BA_.v1.xlsx
.. _NASA-Landsat-9-TIRS: https://landsat.gsfc.nasa.gov/wp-content/uploads/2021-10/L9_TIRS2_Relative_Spectral_Responses.BA.v1.0.xlsx
.. _NESDIS: https://ncc.nesdis.noaa.gov/J1VIIRS/J1VIIRSSpectralResponseFunctions.php
.. _CMA: http://www.cma.gov.cn/en2014/
.. _NWPSAF-MetImage: https://nwpsaf.eu/downloads/rtcoef_rttov12/ir_srf/rtcoef_metopsg_1_metimage_srf.html
.. _NWPSAF-GeoKompsat-2A-ami: https://nwpsaf.eu/downloads/rtcoef_rttov12/ir_srf/rtcoef_gkompsat2_1_ami_srf.html
.. _NWPSAF-Meteosat-12-fci: https://nwpsaf.eu/downloads/rtcoef_rttov12/ir_srf/rtcoef_mtg_1_fci_srf.html
.. _NSMC-fy4a: http://fy4.nsmc.org.cn/portal/cn/fycv/srf.html
