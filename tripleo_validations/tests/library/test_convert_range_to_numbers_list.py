# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest.mock import MagicMock
from unittest.mock import patch

import library.convert_range_to_numbers_list as validation
from tripleo_validations.tests import base


class TestConvertRangeToNumbersList(base.TestCase):

    def setUp(self):
        super(TestConvertRangeToNumbersList, self).setUp()
        self.module = MagicMock()

    def test_valid_convert_range_to_numbers_list(self):
        range_list = "2-5,8-11"
        expected_value = [2, 3, 4, 5, 8, 9, 10, 11]
        result = validation.convert_range_to_numbers_list(self.module, range_list)
        self.assertEqual(result, expected_value)

    def test_valid_convert_range_to_numbers_list_with_exclude_value(self):
        range_list = "2-5,8-11,^8"
        expected_value = [2, 3, 4, 5, 9, 10, 11]
        result = validation.convert_range_to_numbers_list(self.module, range_list)
        self.assertEqual(result, expected_value)

    def test_invalid_convert_range_to_numbers_list(self):
        range_list = "2-5,-"
        validation.convert_range_to_numbers_list(self.module, range_list)
        self.module.fail_json.assert_called_with(
            msg="Invalid number in input param 'range_list': invalid literal for int() with base 10: ''")
