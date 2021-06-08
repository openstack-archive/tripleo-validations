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
test_icmp_ping
----------------------------------

Tests for `icmp_ping` module.
"""

try:
    from unittest import mock
except ImportError:
    import mock

from tripleo_validations.tests import base
from tripleo_validations.tests import fakes

import library.icmp_ping as validation


class TestIcmpPing(base.TestCase):

    def setUp(self):
        self.tested_module = validation
        return super().setUp()

    def test_module_init(self):
        module_attributes = dir(self.tested_module)

        required_attributes = [
            'DOCUMENTATION',
            'EXAMPLES']

        self.assertTrue(set(required_attributes).issubset(module_attributes))

    @mock.patch(
        'library.icmp_ping.yaml_safe_load',
        return_value={'options': 'foo'})
    @mock.patch('library.icmp_ping.AnsibleModule')
    def test_successful_ping(self, mock_module, mock_yaml_load):
        """Test successful ping call with dummy stdout and stderr.
        Calls to the code handling the actual network comms are mocked.
        """
        ansible_module = mock.MagicMock(
            run_command=mock.MagicMock(
                return_value=[0, "fizz", "buzz"]),
            autospec=True)

        mock_module.return_value = ansible_module
        self.tested_module.main()

        ansible_module.exit_json.assert_called_once_with(
            changed=False,
            failed=False,
            msg="fizz")

    @mock.patch(
        'library.icmp_ping.yaml_safe_load',
        return_value={'options': 'foo'})
    @mock.patch('library.icmp_ping.AnsibleModule')
    def test_success_no_stdout(self, mock_module, mock_yaml_load):
        """Test successful ping call  that didn't produce and stdout.
        Calls to the code handling the actual network comms are mocked.
        """

        ansible_module = mock.MagicMock(
            run_command=mock.MagicMock(
                return_value=[0, None, "buzz"]))

        mock_module.return_value = ansible_module
        self.tested_module.main()

        ansible_module.exit_json.assert_called_once_with(
            changed=False,
            failed=False,
            msg="buzz")

    @mock.patch(
        'library.icmp_ping.yaml_safe_load',
        return_value={'options': 'foo'})
    @mock.patch('library.icmp_ping.AnsibleModule')
    def test_failure(self, mock_module, mock_yaml_load):
        """Test failed ping call with dummy stdout and stderr.
        Calls to the code handling the actual network comms are mocked.
        """
        ansible_module = mock.MagicMock(
            run_command=mock.MagicMock(
                return_value=[1, "fizz", "buzz"]))

        mock_module.return_value = ansible_module
        self.tested_module.main()
        ansible_module.exit_json.assert_called_once_with(
            changed=False,
            failed=True,
            msg="fizz")
