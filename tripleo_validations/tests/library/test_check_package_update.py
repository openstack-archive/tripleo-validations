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
from mock import patch

from library.check_package_update import check_update
from library.check_package_update import get_package_details
from tripleo_validations.tests import base


PKG_INSTALLED = "foo-package|6.1.5|1|x86_64"

PKG_AVAILABLE = """\
Available Packages
foo-package.x86_64        8.0.0-1         foo-stable
"""


class TestGetPackageDetails(base.TestCase):
    def setUp(self):
        super(TestGetPackageDetails, self).setUp()
        self.entry = get_package_details("foo-package|6.2.0|1|x86_64")

    def test_name(self):
        self.assertEqual(self.entry.name, 'foo-package')

    def test_arch(self):
        self.assertEqual(self.entry.arch, 'x86_64')

    def test_version(self):
        self.assertEqual(self.entry.version, '6.2.0')

    def test_release(self):
        self.assertEqual(self.entry.release, '1')


class TestCheckUpdate(base.TestCase):
    def setUp(self):
        super(TestCheckUpdate, self).setUp()
        self.module = MagicMock()

    def test_unsupported_pkg_mgr_fails(self):
        check_update(self.module, 'foo-package', 'apt')
        self.module.fail_json.assert_called_with(
            msg='Package manager "apt" is not supported.')

    @patch('library.check_package_update._command')
    def test_fails_if_installed_package_not_found(self, mock_command):
        mock_command.side_effect = [
            ['', 'No package found.'],
        ]
        check_update(self.module, 'foo-package', 'yum')
        self.module.fail_json.assert_called_with(
            msg='No package found.')

    @patch('library.check_package_update._command')
    def test_returns_current_and_available_versions(self, mock_command):
        mock_command.side_effect = [
            [PKG_INSTALLED, ''],
            [PKG_AVAILABLE, ''],
        ]

        check_update(self.module, 'foo-package', 'yum')
        self.module.exit_json.assert_called_with(changed=False,
                                                 name='foo-package',
                                                 current_version='6.1.5',
                                                 current_release='1',
                                                 new_version='8.0.0',
                                                 new_release='1')

    @patch('library.check_package_update._command')
    def test_returns_current_version_if_no_updates(self, mock_command):
        mock_command.side_effect = [
            [PKG_INSTALLED, ''],
            ['', 'No packages found'],
        ]
        check_update(self.module, 'foo-package', 'yum')
        self.module.exit_json.assert_called_with(changed=False,
                                                 name='foo-package',
                                                 current_version='6.1.5',
                                                 current_release='1',
                                                 new_version=None,
                                                 new_release=None)
