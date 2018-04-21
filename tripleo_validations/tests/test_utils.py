# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import collections

from tripleo_validations.tests import base
from tripleo_validations import utils

PATH = [
    ('properties', collections.Mapping, 'dictionary'),
    ('config', collections.Mapping, 'dictionary'),
    ('network_config', collections.Iterable, 'list'),
]


class TestGetNested(base.TestCase):

    def test_get_nested(self):
        # Test config lookup using current format (t-h-t >= Ocata)
        resources = {
            'properties': {
                'config': {
                    'str_replace': {
                        'params': {
                            '$network_config': {
                                'network_config': [
                                    'current'
                                ]
                            }
                        }
                    }
                }
            }
        }
        self.assertEqual(
            utils.get_nested(resources, 'foo', PATH[:])[0],
            'current')

    def test_get_nested_returns_none_if_not_found(self):
        # get_nested should return None if
        # any of the keys cannot be found in the resources tree:
        # `properties`, `config`, `network_config`
        no_properties = {
            'bar': {
                'config': {
                    'str_replace': {
                        'params': {
                            '$network_config': {
                                'network_config': [
                                    'current'
                                ]
                            }
                        }
                    }
                }
            }
        }
        no_config = {
            'properties': {
                'bar': {
                    'str_replace': {
                        'params': {
                            '$network_config': {
                                'network_config': [
                                    'current'
                                ]
                            }
                        }
                    }
                }
            }
        }
        no_network_config = {
            'properties': {
                'config': {
                    'str_replace': {
                        'params': {
                            '$network_config': {
                                'bar': {
                                    'some': 'val'
                                }
                            }
                        }
                    }
                }
            }
        }
        self.assertEqual(
            utils.get_nested(no_properties, 'foo', PATH[:]), None)
        self.assertEqual(utils.get_nested(no_config, 'foo', PATH[:]), None)
        self.assertEqual(
            utils.get_nested(no_network_config, 'foo', PATH[:]), None)

    def test_get_nested_old_format(self):
        # Test config lookup using format used in t-h-t <= Newton
        resources = {
            'properties': {
                'config': {
                    'os_net_config': {
                        'network_config': [
                            'old'
                        ]
                    }
                }
            }
        }
        self.assertEqual(
            utils.get_nested(resources, 'foo', PATH[:])[0],
            'old')
