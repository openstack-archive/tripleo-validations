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
test_pacemaker
--------------

Tests for the `pacemaker` module.
"""
try:
    from unittest import mock
except ImportError:
    import mock

from tripleo_validations.tests import base
from tripleo_validations.tests import fakes
from library import pacemaker


class TestPacemaker(base.TestCase):
    def setUp(self):
        self.tested_module = pacemaker
        return super().setUp()

    def test_module_init(self):

        expepect_attrs = set(
            [
                'DOCUMENTATION',
                'EXAMPLES',
                'main'])

        actual_attrs = set(dir(pacemaker))

        self.assertTrue(expepect_attrs.issubset(actual_attrs))

    @mock.patch('library.pacemaker.ElementTree.fromstring')
    def test_parse_pcs_status(self, mock_fromstring):
        test_xml = "<foo></foo>"
        return_value = self.tested_module.parse_pcs_status(test_xml)
        mock_fromstring.assert_called_once_with(test_xml)

    def test_format_failure_empty(self):

        return_value = self.tested_module.format_failure({})
        expected_value = (
            "Task None None failed on node None. Exit reason: "
            "'None'. Exit status: 'None'.")
        self.assertEqual(expected_value, return_value)
