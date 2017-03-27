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
from tripleo_validations.tests import base


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
