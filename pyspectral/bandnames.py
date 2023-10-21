#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2023 Pytroll developers
#
#
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

BANDNAMES['agri'] = {'C01': 'ch1',
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

BANDNAMES['fci'] = {'vis_04': 'VIS0.4',
                    'vis_05': 'VIS0.5',
                    'vis_06': 'VIS0.6_HR',
                    'vis_08': 'VIS0.8',
                    'vis_09': 'VIS0.9',
                    'nir_13': 'NIR1.3',
                    'nir_16': 'NIR1.6',
                    'nir_22': 'NIR2.2_HR',
                    'ir_38': 'IR3.8_HR',
                    'wv_63': 'WV6.3',
                    'wv_73': 'WV7.3',
                    'ir_87': 'IR8.7',
                    'ir_97': 'IR9.7',
                    'ir_105': 'IR10.5_HR',
                    'ir_123': 'IR12.3',
                    'ir_133': 'IR13.3'
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

BANDNAMES['VII'] = {'vii_443': 'ch1',
                    'vii_555': 'ch2',
                    'vii_668': 'ch3',
                    'vii_752': 'ch4',
                    'vii_763': 'ch5',
                    'vii_865': 'ch6',
                    'vii_914': 'ch7',
                    'vii_1240': 'ch8',
                    'vii_1375': 'ch9',
                    'vii_1640': 'ch10',
                    'vii_2250': 'ch11',
                    'vii_3740': 'ch12',
                    'vii_3959': 'ch13',
                    'vii_4050': 'ch14',
                    'vii_6725': 'ch15',
                    'vii_7325': 'ch16',
                    'vii_8540': 'ch17',
                    'vii_10690': 'ch18',
                    'vii_12020': 'ch19',
                    'vii_13345': 'ch20',
                    }
