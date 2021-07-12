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

try:
    from unittest import mock
except ImportError:
    import mock

from tripleo_validations.tests import base

from library import tripleo_haproxy_conf


class TestHaproxyConf(base.TestCase):
    def setUp(self):
        super(TestHaproxyConf, self).setUp()
        self.h_conf = tripleo_haproxy_conf

    @mock.patch('library.tripleo_haproxy_conf.generic_ini_style_conf_parser')
    def test_parse_haproxy_conf(self, mock_generic_ini_style_conf_parser):
        """ Despite the appearences this test is not using regex at all.
        These are merely raw strings, that it asserts are passed to the `generic_ini_style_conf_parser`.
        From the pov of the test it is irrelevant what form they have.
        It's the `generic_ini_style_conf_parser` function that is supposed to receive these strings as arguments.
        Test is merely checking that the code immediately preceding it's call does what it should do.
        The regexes are finally used for parsing haproxy.cfg, which has a rather vague syntax.
        In short: The regexes are supposed to match all possibilities described here, and some more:
        https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/load_balancer_administration/ch-haproxy-setup-vsa
        """

        file_path = './foo/bar'

        args = {
            'file_path': file_path,
            'section_regex': r'^(\w+)',
            'option_regex': r'^(?:\s+)(\w+(?:\s+\w+)*?)\s+([\w/]*)$'
        }

        self.h_conf.parse_haproxy_conf(file_path)
        mock_generic_ini_style_conf_parser.assert_called_once_with(
            args['file_path'],
            args['section_regex'],
            args['option_regex']
        )
