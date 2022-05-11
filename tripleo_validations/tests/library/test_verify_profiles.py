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

"""
test_verify_profiles
----------------------------------

Tests for `verify_profiles` module.
"""

try:
    from unittest import mock
except ImportError:
    import mock

from logging import warning
from tripleo_validations.tests import base
from tripleo_validations.tests import fakes

import library.verify_profiles as validation


class TestVerifyProfiles(base.TestCase):

    def setUp(self):
        self.tested_module = validation
        return super().setUp()

    def test_module_init(self):
        module_attributes = dir(self.tested_module)

        required_attributes = [
            'DOCUMENTATION',
            'EXAMPLES']

        self.assertTrue(set(required_attributes).issubset(module_attributes))

    def test_caps_to_dict(self):
        """Test various use cases of the '_capabilities_to_dict' function.
        """
        test_dict = {"foo": "bar", "fizz": "buzz"}
        #Test None => dict "conversion"
        self.assertEqual({}, self.tested_module._capabilities_to_dict(None))

        #Test dict => dict. This isn't a conversion at all, but an identity op
        self.assertEqual(
            test_dict,
            self.tested_module._capabilities_to_dict(test_dict))

        self.assertEqual(
            test_dict,
            self.tested_module._capabilities_to_dict('foo:bar,fizz:buzz'))

    @mock.patch('library.verify_profiles._capabilities_to_dict')
    def test_node_get_capabilities(self, mock_dict_conv):
        """Test 'node_get_capabilities' function.
        Not much to test, just a call to the '_capabilities_to_dict'.
        """

        self.tested_module._node_get_capabilities(fakes.MOCK_NODES[0])

        mock_dict_conv.assert_called_once_with(
            fakes.MOCK_NODES[0]['properties']['capabilities'])

    @mock.patch(
        'library.verify_profiles.yaml_safe_load',
        return_value={'options': 'foo'})
    @mock.patch(
        'library.verify_profiles.AnsibleModule')
    @mock.patch(
        'library.verify_profiles.verify_profiles',
        return_value=(None, None))
    def test_main_success(self, mock_verify, mock_module, mock_yaml):
        """Test if the module properly sends information about successful run,
        to the 'exit_json' method of the 'AnsibleModule' object.
        """

        returned_module = mock.MagicMock(
            params={
                'nodes': 'fizz',
                'flavors': 'buzz'})
        mock_module.return_value = returned_module
        self.tested_module.main()

        mock_yaml.assert_called_once()
        mock_verify.assert_called_once_with('fizz', 'buzz')
        returned_module.assert_has_calls([
            mock.call.exit_json(msg="No profile errors detected.")])

    @mock.patch(
        'library.verify_profiles.yaml_safe_load',
        return_value={'options': 'foo'})
    @mock.patch(
        'library.verify_profiles.AnsibleModule')
    @mock.patch(
        'library.verify_profiles.verify_profiles',
        return_value=(None, ['HCF']))
    def test_main_errors(self, mock_verify, mock_module, mock_yaml):
        """Test if the module properly sends information about error,
        such as the catastrophic temperature increase, to the 'fail_json'
        method of the 'AnsibleModule' object.
        """

        returned_module = mock.MagicMock(
            params={
                'nodes': 'fizz',
                'flavors': 'buzz'})
        mock_module.return_value = returned_module
        self.tested_module.main()

        mock_yaml.assert_called_once()
        mock_verify.assert_called_once_with('fizz', 'buzz')
        returned_module.assert_has_calls([
            mock.call.fail_json(msg="HCF")])

    @mock.patch(
        'library.verify_profiles.yaml_safe_load',
        return_value={'options': 'foo'})
    @mock.patch(
        'library.verify_profiles.AnsibleModule')
    @mock.patch(
        'library.verify_profiles.verify_profiles',
        return_value=(['HCF imminent'], None))
    def test_main_warnings(self, mock_verify, mock_module, mock_yaml):
        """Test if the module properly sends information about warning,
        such as incoming catastrophic temperature increase,
        to the 'exit_json' method of the 'AnsibleModule' object.
        """

        returned_module = mock.MagicMock(
            params={
                'nodes': 'fizz',
                'flavors': 'buzz'})

        mock_module.return_value = returned_module
        self.tested_module.main()

        mock_yaml.assert_called_once()
        mock_verify.assert_called_once_with('fizz', 'buzz')

        returned_module.assert_has_calls([
            mock.call.exit_json(warnings="HCF imminent")])

    def test_verify_profiles_success(self):

        return_value = self.tested_module.verify_profiles(
            [fakes.MOCK_NODES[0]],
            fakes.MOCK_PROFILE_FLAVORS)

        self.assertEqual(return_value, ([], []))

    def test_verify_profiles_warning_overcount(self):
        warn_msg = "1 nodes with profile None won't be used for deployment now"
        return_value = self.tested_module.verify_profiles(
            fakes.MOCK_NODES,
            fakes.MOCK_PROFILE_FLAVORS)

        self.assertEqual(([warn_msg], []), return_value)
