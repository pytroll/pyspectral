#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Adam.Dybbroe

# Author(s):

#   Adam Dybbroe <Firstname.Lastname@smhi.se>

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

"""Band name translations."""

BANDNAMES = {}
BANDNAMES['generic'] = {'VIS006': 'VIS0.6',
                        'VIS008': 'VIS0.8',
                        'IR_016': 'NIR1.6',
                        'IR_039': 'IR3.9',
                        'WV_062': 'IR6.2',
                        'WV_073': 'IR7.3',
                        'IR_087': 'IR8.7',
                        'IR_097': 'IR9.7',
                        'IR_108': 'IR10.8',
                        'IR_120': 'IR12.0',
                        'IR_134': 'IR13.4',
                        'HRV': 'HRV',
                        'I01': 'I1',
                        'I02': 'I2',
                        'I03': 'I3',
                        'I04': 'I4',
                        'I05': 'I5',
                        'M01': 'M1',
                        'M02': 'M2',
                        'M03': 'M3',
                        'M04': 'M4',
                        'M05': 'M5',
                        'M06': 'M6',
                        'M07': 'M7',
                        'M08': 'M8',
                        'M09': 'M9',
                        'C01': 'ch1',
                        'C02': 'ch2',
                        'C03': 'ch3',
                        'C04': 'ch4',
                        'C05': 'ch5',
                        'C06': 'ch6',
                        'C07': 'ch7',
                        'C08': 'ch8',
                        'C09': 'ch9',
                        'C10': 'ch10',
                        'C11': 'ch11',
                        'C12': 'ch12',
                        'C13': 'ch13',
                        'C14': 'ch14',
                        'C15': 'ch15',
                        'C16': 'ch16',
                        }
# handle arbitrary channel numbers
for chan_num in range(1, 37):
    BANDNAMES['generic'][str(chan_num)] = 'ch{:d}'.format(chan_num)

# MODIS RSR files were made before 'chX' became standard in pyspectral
BANDNAMES['modis'] = {str(chan_num): str(chan_num) for chan_num in range(1, 37)}

BANDNAMES['seviri'] = {'VIS006': 'VIS0.6',
                       'VIS008': 'VIS0.8',
                       'IR_016': 'NIR1.6',
                       'IR_039': 'IR3.9',
                       'WV_062': 'IR6.2',
                       'WV_073': 'IR7.3',
                       'IR_087': 'IR8.7',
                       'IR_097': 'IR9.7',
                       'IR_108': 'IR10.8',
                       'IR_120': 'IR12.0',
                       'IR_134': 'IR13.4',
                       'HRV': 'HRV'}

BANDNAMES['viirs'] = {'I01': 'I1',
                      'I02': 'I2',
                      'I03': 'I3',
                      'I04': 'I4',
                      'I05': 'I5',
                      'M01': 'M1',
                      'M02': 'M2',
                      'M03': 'M3',
                      'M04': 'M4',
                      'M05': 'M5',
                      'M06': 'M6',
                      'M07': 'M7',
                      'M08': 'M8',
                      'M09': 'M9',
                      }

BANDNAMES['avhrr-3'] = {'1': 'ch1',
                        '2': 'ch2',
                        '3b': 'ch3b',
                        '3a': 'ch3a',
                        '4': 'ch4',
                        '5': 'ch5'}

BANDNAMES['abi'] = {'C01': 'ch1',
                    'C02': 'ch2',
                    'C03': 'ch3',
                    'C04': 'ch4',
                    'C05': 'ch5',
                    'C06': 'ch6',
                    'C07': 'ch7',
                    'C08': 'ch8',
                    'C09': 'ch9',
                    'C10': 'ch10',
                    'C11': 'ch11',
                    'C12': 'ch12',
                    'C13': 'ch13',
                    'C14': 'ch14',
                    'C15': 'ch15',
                    'C16': 'ch16'
                    }

BANDNAMES['ahi'] = {'B01': 'ch1',
                    'B02': 'ch2',
                    'B03': 'ch3',
                    'B04': 'ch4',
                    'B05': 'ch5',
                    'B06': 'ch6',
                    'B07': 'ch7',
                    'B08': 'ch8',
                    'B09': 'ch9',
                    'B10': 'ch10',
                    'B11': 'ch11',
                    'B12': 'ch12',
                    'B13': 'ch13',
                    'B14': 'ch14',
                    'B15': 'ch15',
                    'B16': 'ch16'
                    }

BANDNAMES['ami'] = {'VI004': 'ch1',
                    'VI005': 'ch2',
                    'VI006': 'ch3',
                    'VI008': 'ch4',
                    'NR013': 'ch5',
                    'NR016': 'ch6',
                    'SW038': 'ch7',
                    'WV063': 'ch8',
                    'WV069': 'ch9',
                    'WV073': 'ch10',
                    'IR087': 'ch11',
                    'IR096': 'ch12',
                    'IR105': 'ch13',
                    'IR112': 'ch14',
                    'IR123': 'ch15',
                    'IR133': 'ch16'
                    }

BANDNAMES['fci'] = {'vis_04': 'ch1',
                    'vis_05': 'ch2',
                    'vis_06': 'ch3',
                    'vis_08': 'ch4',
                    'vis_09': 'ch5',
                    'nir_13': 'ch6',
                    'nir_16': 'ch7',
                    'nir_22': 'ch8',
                    'ir_38': 'ch9',
                    'wv_63': 'ch10',
                    'wv_73': 'ch11',
                    'ir_87': 'ch12',
                    'ir_97': 'ch13',
                    'ir_105': 'ch14',
                    'ir_123': 'ch15',
                    'ir_133': 'ch16'
                    }

BANDNAMES['slstr'] = {'S1': 'ch1',
                      'S2': 'ch2',
                      'S3': 'ch3',
                      'S4': 'ch4',
                      'S5': 'ch5',
                      'S6': 'ch6',
                      'S7': 'ch7',
                      'S8': 'ch8',
                      'S9': 'ch9',
                      'F1': 'ch7',
                      'F2': 'ch8',
                      }
