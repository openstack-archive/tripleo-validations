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
test_undercloud_conf
----------------------------------

Tests for `undercloud_conf` module.
"""

import os
import tempfile

from tripleo_validations.tests import base
import validations.library.undercloud_conf as validation


missing_section_content = 'hello world'

valid_content = '''
[DEFAULT]
debug=True

[dhcp]
dhcp_start=192.168.0.1
dhcp_end=192.168.0.254

[secrets]
password=1234
'''

parsing_error_content = '''
[DEFAULT]
    debug =

    [ip
'''

valid_result = {'DEFAULT': {'debug': 'True'},
                'dhcp': {'debug': 'True',
                         'dhcp_end': '192.168.0.254',
                         'dhcp_start': '192.168.0.1'},
                'secrets': {'debug': 'True',
                            'password': '1234'}}


class TestUndercloudConf(base.TestCase):

    def test_check_arguments_invalid_path(self):
        '''Test undercloud_conf when path is invalid'''

        exists, errors = validation.check_arguments('non/existing/path', False)
        self.assertEqual(False, exists)
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0], 'Could not open the undercloud.conf file' +
                         ' at non/existing/path')

    def test_check_arguments_valid_path(self):
        '''Test undercloud_conf when path is valid'''

        tmpfile = self.create_tmp_undercloud_conf()
        tmp_name = os.path.relpath(tmpfile.name)
        exists, errors = validation.check_arguments(tmp_name, False)
        tmpfile.close()

        self.assertEqual(True, exists)
        self.assertEqual([], errors)

    def test_check_arguments_ignore_missing_invalid_path(self):
        '''Test undercloud_conf when ignore_missing is set, path is invalid'''

        exists, errors = validation.check_arguments('non/existing/path', True)
        self.assertEqual(False, exists)
        self.assertEqual([], errors)

    def test_check_arguments_ignore_missing_valid_path(self):
        '''Test undercloud_conf when ignore_missing is set, path is valid'''

        tmpfile = self.create_tmp_undercloud_conf()
        tmp_name = os.path.relpath(tmpfile.name)
        exists, errors = validation.check_arguments(tmp_name, True)
        tmpfile.close()

        self.assertEqual(True, exists)
        self.assertEqual([], errors)

    def test_get_result_missing_section_headers(self):
        '''Test undercloud_conf when content format is invalid'''

        tmpfile = self.create_tmp_undercloud_conf()
        tmp_name = os.path.relpath(tmpfile.name)
        tmpfile.write(missing_section_content.encode('utf-8'))
        tmpfile.seek(0)
        errors, result = validation.get_result(tmp_name)
        tmpfile.close()

        self.assertEqual({}, result)
        self.assertEqual(1, len(errors))
        self.assertEqual('File contains no section headers.', errors[0])

    def test_get_result_parsing_error(self):
        '''Test undercloud_conf when content format is invalid'''

        tmpfile = self.create_tmp_undercloud_conf()
        tmp_name = os.path.relpath(tmpfile.name)
        tmpfile.write(parsing_error_content.encode('utf-8'))
        tmpfile.seek(0)
        errors, result = validation.get_result(tmp_name)
        tmpfile.close()

        self.assertEqual({}, result)
        self.assertEqual(1, len(errors))
        self.assertEqual('File contains parsing errors.', errors[0])

    def test_get_result_valid_file(self):
        '''Test undercloud_conf when content format is valid'''

        tmpfile = self.create_tmp_undercloud_conf()
        tmp_name = os.path.relpath(tmpfile.name)
        tmpfile.write(valid_content.encode('utf-8'))
        tmpfile.seek(0)
        errors, result = validation.get_result(tmp_name)
        tmpfile.close()

        self.assertEqual(valid_result, result)
        self.assertEqual([], errors)

    def create_tmp_undercloud_conf(self):
        '''Create temporary undercloud.conf file, return its full name'''
        path = 'tripleo_validations/tests'
        tmpfile = tempfile.NamedTemporaryFile(suffix='.conf',
                                              prefix='undercloud', dir=path)
        return tmpfile
