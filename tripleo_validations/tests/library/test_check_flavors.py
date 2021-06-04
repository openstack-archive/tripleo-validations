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
test_check_flavors
--------------

Tests for the `check_flavors` module.
"""
try:
    from unittest import mock
except ImportError:
    import mock

from tripleo_validations.tests import base
from tripleo_validations.tests import fakes
from library import check_flavors


class TestCheckFlavors(base.TestCase):

    def setUp(self):
        self.tested_module = check_flavors
        return super().setUp()

    def test_module_init(self):

        expepect_attrs = set(
            [
                'DOCUMENTATION',
                'EXAMPLES',
                'main'])

        actual_attrs = set(dir(self.tested_module))

        self.assertTrue(expepect_attrs.issubset(actual_attrs))

    def test_validate_roles_and_flavors(self):
        expected_values = fakes.MOCK_FLAVORS_CHECK_EXPECTED['ok']

        return_value = self.tested_module.validate_roles_and_flavors(
            fakes.MOCK_ROLES_INFO,
            fakes.MOCK_FLAVORS['ok'])
        self.assertEqual(expected_values, return_value)

    def test_validate_roles_and_flavors_nocpu(self):
        """Tests situation when the 'VCPU' key doesn't have associated value.
        'DISK_GB' and 'MEMORY_MB' behave the same way,
        so we don't need to test them. For now at least.
        """
        expected_values = fakes.MOCK_FLAVORS_CHECK_EXPECTED['fail_NOVCPU']

        return_value = self.tested_module.validate_roles_and_flavors(
            fakes.MOCK_ROLES_INFO,
            fakes.MOCK_FLAVORS['fail_NOVCPU'])
        self.assertEqual(expected_values, return_value)
