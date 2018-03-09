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
test_ini
----------------------------------

Tests for `ini` module.
"""


import os
import tempfile

from tripleo_validations.tests import base
import validations.library.ini as validation


invalid_content = '''
[DEFAULT#
    hello =
'''

valid_content = '''
[DEFAULT]
debug=True

[dhcp]
dhcp_start=192.168.0.1
dhcp_end=192.168.0.254

[secrets]
password=1234
'''


class TestIni(base.TestCase):

    def test_check_file_invalid_path(self):
        '''Test ini when path is invalid'''

        msg = validation.check_file('non/existing/path', False)
        self.assertEqual("Could not open the ini file: 'non/existing/path'",
                         msg)

    def test_check_file_ignore_missing(self):
        '''Test ini when ignoring missing files'''

        msg = validation.check_file('non/existing/path', True)
        self.assertEqual("Could not open the ini file: 'non/existing/path'",
                         msg)

    def test_check_file_valid_path(self):
        '''Test ini when path is valid'''

        tmpfile = self.create_tmp_ini()
        tmp_name = os.path.relpath(tmpfile.name)
        msg = validation.check_file(tmp_name, False)
        tmpfile.close()

        self.assertEqual('', msg)

    def test_get_result_invalid_format(self):
        '''Test ini when file format is valid'''

        tmpfile = self.create_tmp_ini()
        tmp_name = os.path.relpath(tmpfile.name)
        tmpfile.write(invalid_content.encode('utf-8'))
        tmpfile.seek(0)
        ret, msg, value = validation.get_result(tmp_name, 'section', 'key')
        tmpfile.close()

        self.assertEqual(validation.ReturnValue.INVALID_FORMAT, ret)
        self.assertEqual("The file '{}' is not in a valid INI format.".format(
                         tmp_name), msg)
        self.assertIsNone(value)

    def test_get_result_key_not_found(self):
        '''Test ini when key is not found'''

        tmpfile = self.create_tmp_ini()
        tmp_name = os.path.relpath(tmpfile.name)
        tmpfile.write(valid_content.encode('utf-8'))
        tmpfile.seek(0)
        ret, msg, value = validation.get_result(tmp_name, 'section', 'key')
        tmpfile.close()

        self.assertEqual(validation.ReturnValue.KEY_NOT_FOUND, ret)
        self.assertEqual(("There is no key 'key' under the section 'section' "
                          "in file {}.").format(tmp_name), msg)
        self.assertIsNone(value)

    def test_get_result_ok(self):
        '''Test ini when key is not found'''

        tmpfile = self.create_tmp_ini()
        tmp_name = os.path.relpath(tmpfile.name)
        tmpfile.write(valid_content.encode('utf-8'))
        tmpfile.seek(0)
        ret, msg, value = validation.get_result(tmp_name, 'secrets',
                                                'password')
        tmpfile.close()

        self.assertEqual(validation.ReturnValue.OK, ret)
        self.assertEqual(("The key 'password' under the section 'secrets'"
                          " in file {} has the value: '1234'").format(
                         tmp_name), msg)
        self.assertEqual('1234', value)

    def create_tmp_ini(self):
        '''Create temporary tmp.ini file, return its full name'''

        path = 'tripleo_validations/tests'
        tmpfile = tempfile.NamedTemporaryFile(suffix='.ini', prefix='tmp',
                                              dir=path)
        return tmpfile
