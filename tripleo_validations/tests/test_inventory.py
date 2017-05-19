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

from mock import MagicMock

from tripleo_validations.inventory import StackOutputs
from tripleo_validations.inventory import TripleoInventory
from tripleo_validations.tests import base


MOCK_ENABLED_SERVICES = {
    "ObjectStorage": [
        "kernel",
        "swift_storage",
        "tripleo_packages"
    ],
    "Controller": [
        "kernel",
        "keystone",
        "tripleo_packages"
    ],
    "Compute": [
        "nova_compute",
        "kernel",
        "tripleo_packages"
    ],
    "CephStorage": [
        "kernel",
        "tripleo_packages"
    ],
    "BlockStorage": [
        "cinder_volume",
        "kernel",
        "tripleo_packages"
    ]
}


class TestInventory(base.TestCase):

    def test_get_roles_by_service(self):
        services = TripleoInventory.get_roles_by_service(
            MOCK_ENABLED_SERVICES)
        expected = {
            'kernel': ['BlockStorage', 'CephStorage', 'Compute', 'Controller',
                       'ObjectStorage'],
            'swift_storage': ['ObjectStorage'],
            'tripleo_packages': ['BlockStorage', 'CephStorage', 'Compute',
                                 'Controller', 'ObjectStorage'],
            'keystone': ['Controller'],
            'nova_compute': ['Compute'],
            'cinder_volume': ['BlockStorage'],
        }
        self.assertDictEqual(services, expected)


class TestStackOutputs(base.TestCase):

    def setUp(self):
        super(TestStackOutputs, self).setUp()
        self.hclient = MagicMock()
        self.hclient.stacks.output_list.return_value = dict(
            outputs=[{'output_key': 'EnabledServices'},
                     {'output_key': 'KeystoneURL'}])
        self.outputs = StackOutputs('overcloud', self.hclient)

    def test_valid_key_calls_api(self):
        expected = 'http://localhost:5000/v3'
        self.hclient.stacks.output_show.return_value = dict(output=dict(
            output_value=expected))
        self.assertEqual(self.outputs['KeystoneURL'], expected)
        # This should also support the get method
        self.assertEqual(self.outputs.get('KeystoneURL'), expected)
        self.assertTrue(self.hclient.called_once_with('overcloud',
                                                      'KeystoneURL'))

    def test_invalid_key_raises_keyerror(self):
        self.assertRaises(KeyError, lambda: self.outputs['Invalid'])

    def test_get_method_returns_default(self):
        default = 'default value'
        self.assertEqual(self.outputs.get('Invalid', default), default)

    def test_iterating_returns_list_of_output_keys(self):
        self.assertEqual([o for o in self.outputs],
                         ['EnabledServices', 'KeystoneURL'])
