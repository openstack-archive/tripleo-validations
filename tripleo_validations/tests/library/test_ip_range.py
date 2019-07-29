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
test_ip_range
----------------------------------

Tests for `ip_range` module.
"""

import library.ip_range as validation
from tripleo_validations.tests import base


class TestIPRange(base.TestCase):

    def test_check_arguments_non_IP(self):
        '''Test ip_range when start is not an IP'''
        errors = validation.check_arguments('something', '192.168.0.1', 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Argument start (something) must be an IP', errors[0])

    def test_check_arguments_IP_versions(self):
        '''Test ip_range when start is IPv4 and end is IPv6'''
        errors = validation.check_arguments('191.168.0.1', '::1', 2)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Arguments start, end must share the same IP version',
                         errors[0])

    def test_check_arguments_neg_range(self):
        '''Test ip_range when min_size is a negative number'''
        errors = validation.check_arguments('192.168.0.1', '192.168.0.2', -3)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Argument min_size(-3) must be greater than 0',
                         errors[0])

    def test_check_arguments_IPv4_ok(self):
        '''Test ip_range on valid IPv4 arguments'''
        errors = validation.check_arguments('192.168.0.1', '192.169.0.254', 5)
        self.assertEqual(errors, [])

    def test_check_arguments_IPv6_ok(self):
        '''Test ip_range on valid IPv6 arguments'''
        errors = validation.check_arguments('2001:d8::1', '2001:d8::1:1', 120)
        self.assertEqual(errors, [])

    def test_check_IP_range_too_small(self):
        '''Test ip_range when range is less than minimal'''
        errors = validation.check_IP_range('192.168.0.1', '192.168.0.5', 6)
        self.assertEqual(len(errors), 2)
        self.assertEqual(
            'The IP range 192.168.0.1 - 192.168.0.5 contains 5 addresses.',
            errors[0]
        )
        self.assertEqual(
            'This might not be enough for the deployment or later scaling.',
            errors[1]
        )

    def test_check_lower_bound_greater_than_upper(self):
        """Test ip_range when lower IP bound is greater than upper"""
        errors = validation.check_arguments('192.168.0.10', '192.168.0.1', 5)
        self.assertEqual(len(errors), 1)
        self.assertEqual("Lower IP bound (192.168.0.10) must be smaller than "
                         "upper bound (192.168.0.1)", errors[0])
