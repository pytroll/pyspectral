#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2019 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <adam.dybbroe@smhi.se>

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

"""A very basic (example) plotting program to display spectral responses for a
set of satellite instruments for a give wavelength range

"""

import matplotlib.pyplot as plt
from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.utils import get_bandname_from_wavelength
from pyspectral.utils import logging_on, logging_off, get_logger
import numpy as np


def plot_band(plt_in, band_name, rsr_obj, **kwargs):
    """Do the plotting of one band"""
    if 'platform_name_in_legend' in kwargs:
        platform_name_in_legend = kwargs['platform_name_in_legend']
    else:
        platform_name_in_legend = False

    detectors = rsr_obj.rsr[band_name].keys()
    # for det in detectors:
    det = sorted(detectors)[0]
    resp = rsr_obj.rsr[band_name][det]['response']
    wvl = rsr_obj.rsr[band_name][det]['wavelength']

    resp = np.ma.masked_less_equal(resp, minimum_response)
    wvl = np.ma.masked_array(wvl, resp.mask)
    resp.compressed()
    wvl.compressed()

    if platform_name_in_legend:
        plt_in.plot(wvl, resp, label='{platform} - {band}'.format(
            platform=rsr_obj.platform_name, band=band_name))
    else:
        plt_in.plot(wvl, resp, label='{band}'.format(band=band_name))

    return plt_in


def get_arguments():
    """Get the command line arguments"""
    import argparse
    parser = argparse.ArgumentParser(
        description='Plot spectral responses for a set of satellite imagers')

    parser.add_argument("--platform_name", '-p', nargs='*',
                        help="The Platform name",
                        type=str, required=True)
    parser.add_argument("--sensor", '-s', nargs='*',
                        help="The sensor/instrument name",
                        type=str, required=True)
    parser.add_argument("-x", "--xlimits", nargs=2,
                        help=("x-axis boundaries for plot"),
                        default=None, type=float)
    parser.add_argument("-y", "--ylimits", nargs=2,
                        help=("y-axis boundaries for plot"),
                        default=None, type=float)
    parser.add_argument("-t", "--minimum_response",
                        help=("Minimum response: Any response lower than " +
                              "this will be ignored when plotting"),
                        default=0.015, type=float)

    parser.add_argument("-no_platform_name_in_legend", help=("No platform name in legend"),
                        action='store_true')
    parser.add_argument("--title", help=("Plot title"),
                        default=None, type=str)
    parser.add_argument("--wavelength_resolution",
                        help=("The step in wavelength (nanometers) when scanning\n" +
                              " the spectral range trying to find bands"),
                        default=0.005, type=float)
    parser.add_argument("-o", "--filename", help=("Output plot file name"),
                        default=None, type=str)
    parser.add_argument(
        "-v", '--verbose', help=("Turn logging on"), action='store_true')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bandname", '-b',
                       help="The sensor band name", type=str)
    group.add_argument("--wavelength", "-w", type=float,
                       help='the approximate spectral wavelength in micron')
    group.add_argument("--range", "-r", nargs='*',
                       help="The wavelength range for the plot",
                       default=[None, None], type=float)

    return parser.parse_args()


if __name__ == "__main__":
    import sys

    args = get_arguments()

    LOG = get_logger(__name__)

    platform_names = args.platform_name
    sensors = args.sensor
    minimum_response = args.minimum_response
    xlimits = args.xlimits
    ylimits = args.ylimits
    title = args.title
    if not title:
        title = 'Relative Spectral Responses'
    filename = args.filename
    no_platform_name_in_legend = args.no_platform_name_in_legend
    wavel_res = args.wavelength_resolution
    verbose = args.verbose

    if verbose:
        logging_on()
    else:
        logging_off()

    req_wvl = None
    band = None
    wvlmin, wvlmax = args.range
    if args.bandname:
        band = args.bandname
    elif args.wavelength:
        req_wvl = args.wavelength

    figscale = 1.0
    if wvlmin:
        figscale = (wvlmax - wvlmin) / 4.
    figsize = (figscale * 1. + 10, figscale * 0.5 + 5)

    plt.figure(figsize=figsize)
    something2plot = False

    for platform in platform_names:
        for sensor in sensors:
            try:
                rsr = RelativeSpectralResponse(platform, sensor)
            except IOError:
                # LOG.exception('Failed getting the rsr data for platform %s ' +
                #               'and sensor %s', platform, sensor)
                rsr = None
            else:
                break

        if not rsr:
            continue

        something2plot = True
        LOG.debug("Platform name %s and Sensor: %s", str(rsr.platform_name), str(rsr.instrument))

        if req_wvl:
            bands = get_bandname_from_wavelength(sensor, req_wvl, rsr.rsr, 0.25, multiple_bands=True)
            if not bands:
                continue
            if isinstance(bands, list):
                for b__ in bands:
                    plt = plot_band(plt, b__, rsr,
                                    platform_name_in_legend=(not no_platform_name_in_legend))
            else:
                plt = plot_band(plt, bands, rsr,
                                platform_name_in_legend=(not no_platform_name_in_legend))

        elif band:
            plt = plot_band(plt, band, rsr,
                            platform_name_in_legend=(not no_platform_name_in_legend))

        else:
            wvlx = wvlmin
            prev_band = None
            while wvlx < wvlmax:
                bands = get_bandname_from_wavelength(sensor, wvlx, rsr.rsr, wavel_res, multiple_bands=True)

                if isinstance(bands, list):
                    b__ = bands[0]
                    for b in bands[1:]:
                        LOG.warning("Skipping band %s", str(b))
                else:
                    b__ = bands

                wvlx = wvlx + wavel_res / 5.
                if not b__:
                    continue
                if b__ != prev_band:
                    plt = plot_band(plt, b__, rsr,
                                    platform_name_in_legend=(not no_platform_name_in_legend))
                    prev_band = b__

    if not something2plot:
        LOG.error("Nothing to plot!")
        sys.exit(0)

    wmin, wmax = plt.xlim()
    delta_x = (wmax - wmin)
    wmax = wmax + delta_x / 4.0
    if xlimits:
        wmin = xlimits[0]
        wmax = xlimits[1]

    plt.xlim((wmin, wmax))

    wmin, wmax = plt.ylim()
    if ylimits:
        wmin = ylimits[0]
        wmax = ylimits[1]

    plt.ylim((wmin, wmax))

    plt.title(title)
    plt.legend(loc='lower right')
    if filename:
        plt.savefig(filename)
    else:
        if req_wvl:
            plt.savefig('rsr_band_{:>04d}.png'.format(int(100 * req_wvl)))
        elif wvlmin and wvlmax:
            plt.savefig('rsr_band_{:>04d}_{:>04d}.png'.format(
                int(100 * wvlmin), int(100 * wvlmax)))
        else:
            plt.savefig('rsr_band_{bandname}.png'.format(bandname=band))
