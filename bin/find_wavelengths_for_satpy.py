#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020-2022 Pytroll developers
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

"""Retrieve channel wavelength ranges for a given sensor."""

import argparse

from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import get_wave_range


def _setup_argparse():
    arg_parser = argparse.ArgumentParser(
        description='Retrieve channel wavelength ranges for a given sensor.')
    arg_parser.add_argument("platform_name",
                            help="The Platform name",
                            type=str)
    arg_parser.add_argument("sensor",
                            help="The sensor/instrument name",
                            type=str)
    arg_parser.add_argument("-r", "--minimum_response",
                            help=("Minimum response threshold: Defines the value "
                                  "that the RSR must exceed in order to trigger"
                                  "the minimum or maximum wavelengths."),
                            default=0.15, type=float)
    arg_parser.add_argument("--bandname", '-b',
                            help="The sensor band name. Leave blank to return all bands.", type=str)
    arg_parser.add_argument("--detector", '-d',
                            help="The sensor detector, if not passed will default to det-1",
                            default='det-1', type=str)
    return arg_parser


def main(arguments):
    """Retrieve wavelength range based on user-supplied arguments."""
    platform = arguments.platform_name
    sensor = arguments.sensor
    threshold = arguments.minimum_response

    rsr = RelativeSpectralResponse(platform, sensor)
    if arguments.bandname:
        bands = [arguments.bandname]
    else:
        bands = rsr.band_names
    det = arguments.detector

    for bname in bands:
        wvls = get_wave_range(rsr.rsr[bname][det], threshold)
        print(f'name:  {bname}')
        print(f'  wavelength: [{wvls[0]:5.3f}, {wvls[1]:5.3f}, {wvls[2]:5.3f}]')


if __name__ == "__main__":

    parser = _setup_argparse()
    args = parser.parse_args()
    main(args)
