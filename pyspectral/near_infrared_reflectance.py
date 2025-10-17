#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2022 Pytroll developers
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Derive NIR reflectances of a a band in the 3-4 micron window region.

Derive the Near-Infrared reflectance of a given band in the solar and
thermal range (usually the 3.7-3.9 micron band) using a thermal atmospheric
window channel (usually around 11-12 microns).
"""

import logging
import os
import tempfile

import numpy as np

try:
    from dask.array import asanyarray, isnan, logical_or, where
except ImportError:
    from numpy import where, logical_or, asanyarray, isnan

from pyspectral.config import get_config
from pyspectral.radiance_tb_conversion import RadTbConverter
from pyspectral.solar import SolarIrradianceSpectrum
from pyspectral.utils import BANDNAMES, WAVE_LENGTH, get_bandname_from_wavelength

LOG = logging.getLogger(__name__)

EPSILON = 0.005
TB_MIN = 150.
TB_MAX = 360.
TERMINATOR_LIMIT = 85.0


class Calculator(RadTbConverter):
    """
    A thermal near-infrared (~3.7 micron) band reflectance calculator.

    Given the relative spectral response of the NIR band, the solar zenith
    angle, and the brightness temperatures of the NIR and the Thermal bands,
    derive the solar reflectance for the NIR band removing the thermal
    (terrestrial) part. The in-band solar flux over the NIR band is
    optional. If not provided, it will be calculated here!

    The relfectance calculated is without units and should be between 0 and 1.
    """

    def __init__(self, platform_name, instrument, band,
                 detector="det-1", wavespace=WAVE_LENGTH,
                 solar_flux=None, sunz_threshold=TERMINATOR_LIMIT, masking_limit=TERMINATOR_LIMIT):
        """Initialize the Class instance."""
        super(Calculator, self).__init__(platform_name, instrument, band, detector=detector, wavespace=wavespace)

        self.bandname = None
        self.bandwavelength = None
        self.detector = detector
        self.lut = None
        self.lutfile = None
        self.masking_limit = masking_limit
        self.solar_flux = solar_flux
        self.sunz_threshold = sunz_threshold
        self._e3x = None
        self._r3x = None
        self._rad3x = None
        self._rad3x_t11 = None
        self._rad3x_correction = 1.0
        self._solar_radiance = None

        self._set_bandname_and_wavelength(band)

        if self.solar_flux is None:
            self._get_solarflux()

        self._set_lutfile()
        self._set_lut()

    def _set_bandname_and_wavelength(self, band):
        from numbers import Number

        if isinstance(band, str):
            self.bandname = BANDNAMES.get(self.instrument, BANDNAMES["generic"]).get(band, band)
            self.bandwavelength = self.rsr[self.bandname]["det-1"]["central_wavelength"]
        elif isinstance(band, Number):
            self.bandwavelength = band
            self.bandname = get_bandname_from_wavelength(self.instrument, band, self.rsr)

        if self.bandwavelength > 3.95 or self.bandwavelength < 3.5:
            raise NotImplementedError("NIR reflectance is not supported outside " +
                                      "the 3.5-3.95 micron interval")

    def _set_lutfile(self):
        options = get_config()
        tb2rad_dir = options.get("tb2rad_dir", tempfile.gettempdir())

        self._lutfile_from_config(options, tb2rad_dir)

        if self.lutfile is None:
            LOG.info("No lut filename available in config file. "
                     "Will generate filename automatically")
            lutname = "tb2rad_lut_{0}_{1}_{band}".format(
                self.platform_name.lower(), self.instrument.lower(), band=self.bandname.lower())
            self.lutfile = os.path.join(tb2rad_dir, lutname + ".npz")

    def _lutfile_from_config(self, options, tb2rad_dir):
        platform_sensor = self.platform_name + "-" + self.instrument

        if platform_sensor in options and "tb2rad_lut_filename" in options[platform_sensor]:
            if isinstance(options[platform_sensor]["tb2rad_lut_filename"], dict):
                self._lutfile_from_dict(options)
            else:
                self.lutfile = options[platform_sensor]["tb2rad_lut_filename"]

            if self.lutfile and not self.lutfile.endswith(".npz"):
                self.lutfile = self.lutfile + ".npz"

            if self.lutfile and not os.path.exists(os.path.dirname(self.lutfile)):
                LOG.warning(
                    "Directory %s does not exist! Check config file", os.path.dirname(self.lutfile))
                self.lutfile = os.path.join(tb2rad_dir, os.path.basename(self.lutfile))

    def _lutfile_from_dict(self, options):
        for item in options[platform_sensor]["tb2rad_lut_filename"]:
            if item == self.bandname or item == self.bandname.lower():
                self.lutfile = options[platform_sensor]["tb2rad_lut_filename"][item]
                break
        if self.lutfile is None:
            LOG.warning("Failed determine LUT filename from config: %s", str(
                options[platform_sensor]["tb2rad_lut_filename"]))

    def _set_lut(self):
        LOG.info("lut filename: " + str(self.lutfile))
        if not os.path.exists(self.lutfile):
            self.make_tb2rad_lut(self.lutfile)
            self.lut = self.read_tb2rad_lut(self.lutfile)
            LOG.info("LUT file created")
        else:
            self.lut = self.read_tb2rad_lut(self.lutfile)
            LOG.info("File was there and has been read!")

    def derive_rad39_corr(self, bt11, bt13, method="rosenfeld"):
        """Derive the CO2 correction to be applied to the 3.9 channel.

        Derive the 3.9 radiance correction factor to account for the
        attenuation of the emitted 3.9 radiance by CO2
        absorption. Requires the 11 micron window band and the 13.4
        CO2 absorption band, as e.g. available on SEVIRI. Currently
        only supports the Rosenfeld method

        """
        if method != "rosenfeld":
            raise AttributeError("Only CO2 correction for SEVIRI using "
                                 "the Rosenfeld equation is supported!")

        LOG.debug("Derive the 3.9 micron radiance CO2 correction coefficent")
        self._rad3x_correction = (bt11 - 0.25 * (bt11 - bt13)) ** 4 / bt11 ** 4

    def _get_solarflux(self):
        """Derive the in-band solar flux from rsr over the Near IR band (3.7 or 3.9 microns)."""
        solar_spectrum = \
            SolarIrradianceSpectrum(dlambda=0.0005,
                                    wavespace=self.wavespace)
        self.solar_flux = solar_spectrum.inband_solarflux(self.rsr[self.bandname])

    def emissive_part_3x(self, tb=True):
        """Get the emissive part of the 3.x band."""
        try:
            # Emissive part:
            self._e3x = self._rad3x_t11 * (1 - self._r3x)
            # Use the original channel data on the night side
            self._e3x = where(isnan(self._e3x), self._rad3x, self._e3x)
            # Unsure how much sense it makes to apply the co2 correction term here!?
            # FIXME!
            # self._e3x *= self._rad3x_correction

        except TypeError:
            LOG.warning(
                "Couldn't derive the emissive part \n" +
                "Please derive the relfectance prior to requesting the emissive part")

        if tb:
            return self.radiance2tb(self._e3x)
        else:
            return self._e3x

    def reflectance_from_tbs(self, sun_zenith, tb_near_ir, tb_thermal, **kwargs):
        """Derive reflectances from Tb's in the 3.x band.

        The relfectance calculated is without units and should be between 0 and 1.

        Inputs:

          sun_zenith: Sun zenith angle for every pixel - in degrees

          tb_near_ir: The 3.7 (or 3.9 or equivalent) IR Tb's at every pixel
                      (Kelvin)

          tb_thermal: The 10.8 (or 11 or 12 or equivalent) IR Tb's at every
                      pixel (Kelvin)

          tb_ir_co2: The 13.4 micron channel (or similar - co2 absorption band)
                     brightness temperatures at every pixel. If None, no CO2
                     absorption correction will be applied.

        """
        if not self.rsr:
            raise NotImplementedError("Reflectance calculations without rsr not yet supported!")

        tb_nir = get_as_array(tb_near_ir)
        tb_therm = get_as_array(tb_thermal)
        if tb_therm.shape != tb_nir.shape:
            raise ValueError(f"Dimensions do not match! {tb_therm.shape} and {tb_nir.shape}")

        # Check for dask arrays
        compute = True
        if hasattr(tb_near_ir, "compute") or hasattr(tb_thermal, "compute"):
            compute = False
        is_masked = False
        if hasattr(tb_near_ir, "mask") or hasattr(tb_thermal, "mask"):
            is_masked = True

        sun_zenith = get_as_array(sun_zenith)
        tb_ir_co2 = kwargs.get("tb_ir_co2")
        lut = kwargs.get("lut", self.lut)

        co2corr = False
        tbco2 = None
        if tb_ir_co2 is not None:
            co2corr = True
            tbco2 = get_as_array(tb_ir_co2)

        # Assume rsr is in microns!!!
        # FIXME!
        self._rad3x_t11 = self.tb2radiance(tb_therm, lut=lut)["radiance"]
        self._rad3x = self.tb2radiance(tb_nir, lut=lut)["radiance"]

        LOG.debug("Apply sun-zenith angle clipping between 0 and %5.2f", self.masking_limit)

        self._calculate_solar_radiance(tb_nir, sun_zenith)
        self._calculate_rad3x_correction(co2corr, tb_therm, tbco2, tb_nir.dtype)

        self._calculate_r3x(tb_therm, sun_zenith, tb_nir)

        res = self._r3x
        if hasattr(self._r3x, "compute") and compute:
            res = self._r3x.compute()
        if is_masked:
            res = np.ma.masked_invalid(res)
        return res

    def _calculate_solar_radiance(self, tb_nir, sun_zenith):
        sunz = sun_zenith.clip(0, self.sunz_threshold)
        mu0 = np.cos(np.deg2rad(sunz))
        # mu0 = np.where(np.less(mu0, 0.1), 0.1, mu0)
        self._solar_radiance = (self.solar_flux * mu0 / np.pi).astype(tb_nir.dtype)

    def _calculate_rad3x_correction(self, co2corr, tb_therm, tbco2, dtype):
        # CO2 correction to the 3.9 radiance, only if tbs of a co2 band around
        # 13.4 micron is provided:
        if co2corr:
            self.derive_rad39_corr(tb_therm, tbco2)
            LOG.info("CO2 correction applied...")
        else:
            self._rad3x_correction = np.float64(1.0)
        self._rad3x_correction = self._rad3x_correction.astype(dtype)

    def _calculate_r3x(self, tb_therm, sun_zenith, tb_nir):
        rsr_integral = tb_therm.dtype.type(self.rsr_integral)
        thermal_emiss_one = self._rad3x_t11 * rsr_integral
        if thermal_emiss_one.ravel().shape[0] < 10:
            LOG.info("thermal_emiss_one = %s", str(thermal_emiss_one))
        corrected_thermal_emiss_one = thermal_emiss_one * self._rad3x_correction
        l_nir = self._rad3x * rsr_integral
        if l_nir.ravel().shape[0] < 10:
            LOG.info("l_nir = %s", str(l_nir))
        nomin = l_nir - corrected_thermal_emiss_one
        denom = self._solar_radiance - corrected_thermal_emiss_one
        data = nomin / denom
        mask = denom < EPSILON

        if self.masking_limit is not None:
            sunzmask = (sun_zenith < 0.0) | (sun_zenith > self.masking_limit)
            logical_or(sunzmask, mask, out=mask)
        logical_or(mask, np.isnan(tb_nir), out=mask)

        self._r3x = where(mask, np.nan, data)


def get_as_array(variable):
    """Return variable as a Dask or Numpy array.

    Variable may be a scalar, a list or a Numpy/Dask array.
    """
    if np.isscalar(variable):
        return asanyarray([variable, ])

    return asanyarray(variable)
