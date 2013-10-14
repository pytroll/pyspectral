
MODIS ProtoFlight Model (PFM) Relative Spectral Response (RSR) Readme File Outline:
 
1.0 Summary of PFM RSR Releases
2.0 RSR Look-Up Table (LUT) I (in-band RSRs as used in L1B V2.2; corrected)
3.0 RSR Reference Table (all data; in-band + OOB; merged and corrected)
4.0 Reference Summary of RSR Center Wavelengths (CWs) and Bandwidths (BWs)
5.0 Notes for the L1B Look-Up-Table (LUT)
6.0 Notes for the RSR Reference Table
7.0 References

1.0 Summary of PFM RSR Releases
Original Release: Dated 2-24-97
Rev A: Dated, 3-6-98
Rev B: Dated, 8-8-98
Rev C: Dated, 4-30-99

General Discussion

PFM RSR Rev. C release incorporates the latest data merging and correction results. Notes in sections 5.0 and 6.0, together with material contained in the references called out in section 7.0 discuss the RSR raw data correction, interpolations, and merging steps. It is intended that this release will be the pre-launch version of the RSR LUT used in the L1B V2.2 Calibration production code. This release contains two (2) versions of the RSR tables:

L1B Look-Up-Table (LUT) contains the In-band RSRs for each of the channels for 36 spectral bands. In-band is defined as the RSR values between the 1% response wavelengths, e.g., 1% low and 1% high. The results will be incorporated into the MCST L1B V2.2 Calibration processing code. It should be noted that the RSR data presented for PFM Band 7, were taken from the FM1 Band 7 measurements, due to the fact that the PFM Band 7 in-band RSR measurements were saturated in the peak response region, preventing accurate determination of the PFM RSR. 

The RSR Reference Table contains the merged In-band and Out-of-Band Dispersive (OOB-D) data sets.  These RSRs contain all measured data, including optical crosstalk features of the PFM and provide an overview of all measured spectral response.  It should be noted that V2.2 of L1B will incorporate data correction, i.e. subtraction routines to partially reduce OOB crosstalk for SWIR bands 5,6 and PC bands 32-36. 

The results presented in L1B Look-Up-Table (LUT) have been corrected for all known biases and aberrations.  At a top level these corrections include:
1) Correction for the GSE Spectroradiometer Measurement Apparatus (SpMA) out-of-plane spectral aberrations (AKA, the smile effect). 
2) SpMA wavelength calibration offsets
3) Atmospheric path absorption corrections 
4) Window absorptions
5) Tfpa (79K->83K) corrections

The results presented in RSR REFERENCE TABLE have also been corrected for all known biases and aberrations. Out-of-Band Dispersive (OOB-D) low spectral resolution measurements have been merged with the high spectral resolution In-band RSR data, for Bands 1-28, following data normalization results provided by SBRS. PFM OOB data are not available for Bands 29-36.  For this reason, FM1 OOB-D are merged with the PFM In-band RSRs to provide some characterization of the OOB regions for these bands.  Since the PFM and FM1 spectral filters were purchased together, there is some basis for this fill-in approach.  Differences between PFM and FM1 dichroics may exist, and could in-principle affect the OOB-D regions somewhat. 

Table A presented in Section 4.0 of this file, summarizes the integrated Center Wavelength (CW) and integrated centroid Bandwidth (BW) for each of the MODIS PFM bands. These results were obtained by integration of the channel-averaged RSRs, i.e., the RSRs from each channel were added, and then divided by the number of channels. 

RSR Corrections Algorithm Flow Chart
A flow diagram of all correction steps taken is provided with this distribution of files in PDF file format.  This file can be found in the /pub/permanent/MCST/PFM_L1B_LUT_4-12-98 directory of the ftp.mcst.ssai.biz ftp server. 


 
Format: Table A (In-Band; corrected))

   Band  Channel          Wavelength (nm)   RSR 
        20       1               3621.40              0.01  (start)
         .         .                     .                   .	
         .         .                     .                   .	
        20       1               3851.58             1.00  (peak)
         .         .                     .                   .	
         .         .                     .                   .	
        20       1               3961.00             0.01  (stop)		
         .         .                     .                   .	
         .         .                     .                   .	
        20       2               3621.40             0.01
         .       .                     .                   .	
         .       .                     .                   .
         .       .                     .                   .	
         .       .                     .                   .	

Format: Table II (All data; Merged and corrected)

   Band      Channel       Wavelength (nm)	  RSR 
        20        1	 	  1100.00             1.7743e-06  (start)
         .          .                    .                       .	
         .          .                    .                       .	
        20       1		  3851.58             1.0             (peak)
         .          .                    .                       .	
         .          .                    .                       .	
        20        1        	  5400.00             1.4691e-05  (stop)	
         .          .                    .                       .	
         .          .                    .                       .	
        20        2                1100.00             1.7341e-06
         .          .                    .                   .	
         .          .                    .                   .




4.0 Center Wavelength and Bandwidths for all MODIS bands 

BW and CW are calculated by integrating over the response between the lower 1% response wavelength and the upper 1% response wavelength.  The all values in the chart below are band averaged.  

 
Band CW (nm)		BW (nm)
      (1%/1%)		        (1%/1%)

---------------------------------------------------------------------------------
B1    646.5			 41.8
B2    856.7			 39.4
B3    465.6			 17.6
B4    553.7			 19.7
B5   1241.9			 24.5
B6   1629.1			 29.7
B7   2114.3                              52.9
B8    411.8	 	 	 11.8
B9    442.1                                9.7
B10   486.9		 	 10.6
B11   529.7		 	 11.8
B12   546.8		 	 10.4
B13   665.6		 	 10.1
B14   676.7		 	 11.4
B15   746.4		 	 10.0
B16   866.2		 	 15.5
B17   904.1		 	 35.7
B18   935.3		 	 13.7
B19   936.1		 	 46.3
B26  1382.0                             36.4
B20  3788.2			182.6		
B21  3992.1                              85.7
B22  3971.9                              88.2
B23  4056.7                              87.8
B24  4473.2		              93.7
B25  4545.4                              94.3
B27  6765.4			254.6
B28  7336.7			325.3
B29  8528.8			369.2
B30  9734.4			300.6
B31 11018.6			510.3
B32 12032.5			493.5
B33 13365.1			306.5
B34 13683.5			322.4
B35 13913.3			333.6
B36 14195.7			268.8



5.0 Notes on Look-Up Table 


I-1:  A correction be made to all grating 4 bands based on the shift detected between the known location of the C02 absorption feature and the perceived notch in the band 35 RSR. Currently our best knowledge of the C02 feature minimum is at 13876 according a LOTRAN model run. The number of RSR points in the band 35 RSR near the C02 absorption feature is limited, so the exact location of the C02 notch can not be determined.  

I-2: Due to SpMA wavelength aberration correction procedure used, the wavelengths set will be different from channel-to-channel.  Also all channels have identically the same center wavelength value due to the SpMA wavelength correction.

I-3: The profile of band 35 relative spectral response profile was adjusted in order to remove the effects caused by the C02 absorption feature.  A simple linear fit was used in order to replace badly affected points in the C02 absorption region.   

I-4: PFM Bands 29-36 were taken under ambient conditions using the Bench Test Cooler (BTC) which held the LWIR focal plane and the filter assembly at 79.6K to 79.9K. Temperature shifts have been applied to bands 27-36.  FM1 shifts were determining the shift in center wavelength measured at NLT and 83K for each band for SWIR, MWIR and LWIR bands.  FM1 shift data was fit to a linear function in order to determine the slope of the correction to apply to PFM RSRs per band.  



6.0 Notes on the RSR Reference Table 

I-1: No valid out-of-band data was available for PFM bands 29-36.  In these cases PFM in-band data was merged with FM1 out-of-band data. Please note that significant PC optical crosstalk does exist for bands 32-36, which is not reflected in these out-of-band data sets borrowed from FM1.  All other MODIS bands have valid PFM out-of-band RSRs included in this data set.  


I-2: The wavelength increments differ between IB and OOB regions, and from band-to-band.  

I-3: The channel-dependent RSRs were merged with the average OOB RSRs, since the OOB measurements were generally noise limited, and therefore the average OOB for that band is believed to be a better representation of the real performance. See Note 4 for two exceptions. 

I-4:  Wherever possible, the average OOB RSR is merged with the channel dependent In-band RSR. However, for band 3 - channel 7 the OOB RSR data was significantly out-of-family from the other 19 channels and therefore the as-measured OOB RSR for this channel was merged with the In-band RSR for that channel. Likewise, Band 16 - Channel 10 out-of-band RSR data was significantly out-of-family from the other 9 channels, and therefore the as-measured OOB RSR for this channel was merged with the In-band RSR for that channel.


I-5: OOB RSRs measured data points near the spectral band pass regions (the wings of the IB RSR) are misleading.  For Bands 23,24, and 25 we extrapolated the IB RSRs down to the 0.001 RSR level to more accurately characterize the true instrument response in the wing regions near the band pass region.      

	
Relative Spectral Response File locations

The described files are available in ASCII format by anonymous ftp on ftp.mcst.ssai.biz in the /pub/permanent/MCST/PFM_L1B_LUT_4-30-99 directory. 
A flow chart describing RSR wavelength correction methodology is available in this directory called RSR_methodology.ppt  (MS PowerPoint format).

The locations for the PFM L1B RSR Look-up-tables is: 
/pub/permanent/MCST/PFM_L1B_LUT_4-30-99/L1B_RSR_LUT
A PDF file called pfm-in-band-rsr.pdf contains plots for all bands. 

PDF files containing plots of this data will be available also in these directories.   


The locations for the PFM Reference (in-band and our-of-band merged) data sets is: 
/pub/permanent/MCST/PFM_L1B_LUT_4-30-99/Reference_RSR_Dataset.  A PDF file called pfm-oob-rsr.pdf contains plots for all bands. 

7.0 References:

Bands PFM Calibration Launch Readiness Review, Dorman, Godden February 3/99,pgs 7-1 to 7-94 
MODIS Science Team Meeting, Relative Spectral Response, T. Dorman, G. Godden October 24,97,pgs 4-1 to 4-65
Spectral calibration gradient along SpMA slits, J.B. Young, 3/18/97,PL3095-N006345
Reflective Bands Relative Spectral Responses (RSR) Along Track Variability,T. Dorman, G. Godden, June 13,1997

