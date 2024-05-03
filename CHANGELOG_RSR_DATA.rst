Changelog for the Relative Spectral Response data
=================================================


Version <v1.3.0> (Fri May  3 04:11:43 PM CEST 2024)
-------------------------------------------

 * Added SRFs (RSRs) for the Mersi-1 sensor onboard FY-3A/B/C
 * Added SRFs for the Mersi-RM sensor onboard FY-3G
 * Added SRFs for the GHI (Geostationary High-speed Imager) sensor onboard FY-4B
 * Added SRFs for GOCI-II (Geostationary Ocean Color Imager: Follow-on) sensor onboard GK-2B (GEO-KOMPSAT-2B)


Version <v1.2.4> (Sat Oct 21 12:25:00 PM CEST 2023)
-------------------------------------------

 * Normalized RSR responses for the EPIC sensor. Now values are sclaed to be
   between 0 and 1.


Version <v1.2.3> (Fri Oct 20 01:58:29 2023)
-------------------------------------------

 * Added RSR file for EPIC on DSCOVR (responses not normalized)


Version <v1.2.2> (Tue Nov 15 14:44:03 2022)
-------------------------------------------

 * Added RSR file for AGRI onboard FY-4B
 * Corrected RSR file for AGRI onboard FY-3B
   Values were between 0 and 100, now scaled to between 0 and 1


Version <v1.2.1> (Mon Oct 24 16:26:14 2022)
-------------------------------------------

 * Changed name of the FY-3D MERSI-2 RSR file, removing the hyphen:
   New name = rsr_mersi2_FY-3D.h5


Version <v1.2.0> (Tue Sep 27 21:08:13 2022)
-------------------------------------------

 * Added VIIRS RSR for JPSS-2/NOAA-21:
   Based on the J2_VIIRS_RSR_DAWG_At-Launch_Public_Release_V2_Jul2019.zip
   The data read are the Detector wise files under J2_VIIRS_Detector_RSR_V2:

   J2_VIIRS_RSR_DNBLGS_Detector_Fused_V2FS.txt
   J2_VIIRS_RSR_I1_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_I2_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_I3_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_I4_Detector_V2F.txt
   J2_VIIRS_RSR_I5_Detector_V2F.txt
   J2_VIIRS_RSR_M10_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M11_Detector_V2F.txt
   J2_VIIRS_RSR_M12_Detector_V2F.txt
   J2_VIIRS_RSR_M13_Detector_V2F.txt
   J2_VIIRS_RSR_M14_Detector_V2F.txt
   J2_VIIRS_RSR_M15_Detector_V2F.txt
   J2_VIIRS_RSR_M16A_Detector_V2F.txt
   J2_VIIRS_RSR_M1_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M2_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M3_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M4_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M5_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M6_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M7_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M8_Detector_Fused_V2F.txt
   J2_VIIRS_RSR_M9_Detector_WVCOR_Fused_V2F.txt

   The two files here were not considered:
   J2_VIIRS_RSR_DNBMGS_Detector_Fused_V2FS.txt
   J2_VIIRS_RSR_M16B_Detector_V2F.txt

 * Correted errors concerning NOAA-6 channel 1 and 2. These proved to be wrong
   (a factor of 10 scale error), as the files they were based on were
   wrong. For AVHRR-1 we have been using the ascii files from NOAA STAR
   (https://www.star.nesdis.noaa.gov/smcd/spb/fwu/homepage/AVHRR/spec_resp_func/index.html). Example
   of the start of the file for NOAA-6 channel-1:

   %> cat NOAA_6_A103C001.txt
      Wavelegth (nm)      Normalized RSF
         5600.000000            0.071000
         5700.000000            0.449000
         5800.000000            0.739000
         5900.000000            0.813000
         6000.000000            0.806000
         6200.000000            0.919000
         6400.000000            1.000000
         ...

   Here we have instead used the xls files on which the NOAA-STAR files are based: AVHRR1_SRF_only.xls

   For TIROS-N there seem to be a typo in the wavelengths array for channel-1
   on TIROS-N: A 640 nm should most likely have been 840 nm. This has been
   corrected in the hdf5 file.
