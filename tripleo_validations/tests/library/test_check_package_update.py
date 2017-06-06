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

from tripleo_validations.tests import base
from validations.library.check_package_update import check_update
from validations.library.check_package_update import get_package_details


PKG_INSTALLED = """\
Last metadata expiration check: 1 day, 3:05:37 ago on Mon Jun  5 11:55:16 2017.
Installed Packages
foo-package.x86_64          2:6.1.5-1          @spideroak-one-stable
"""

# This stretches the boundaries of a realistic yum list output a bit
# but it's more explicit for testing.
PKG_AVAILABLE = """\
Last metadata expiration check: 1 day, 3:06:30 ago on Mon Jun  5 11:55:16 2017.
Available Packages
foo-package.i386              2:9.1.0-1          foo-stable
foo-package.i386              2:6.2.3-1          foo-stable
foo-package.x86_64            2:8.0.0-1          foo-stable
foo-package.x86_64            2:7.0.0-1          foo-stable
foo-package.x86_64            2:6.2.0-1          foo-stable
foo-package.x86_64            2:6.1.6-1          foo-stable
"""


class TestGetPackageDetails(base.TestCase):
    def setUp(self):
        super(TestGetPackageDetails, self).setUp()
        self.entry = get_package_details("""\
foo-package.x86_64            2:6.2.0-1          spideroak-one-stable
""")

    def test_name(self):
        self.assertEqual(self.entry.name, 'foo-package')

    def test_arch(self):
        self.assertEqual(self.entry.arch, 'x86_64')

    def test_version(self):
        self.assertEqual(self.entry.version, '6.2.0')


class TestCheckUpdate(base.TestCase):
    def setUp(self):
        super(TestCheckUpdate, self).setUp()
        self.module = MagicMock()

    def test_unsupported_pkg_mgr_fails(self):
        check_update(self.module, 'foo-package', 'apt')
        self.module.fail_json.assert_called_with(
            msg='Package manager "apt" is not supported.')

    @patch('validations.library.check_package_update._command')
    def test_fails_if_installed_package_not_found(self, mock_command):
        mock_command.side_effect = [
            ['', 'No package found.'],
        ]
        check_update(self.module, 'foo-package', 'yum')
        self.module.fail_json.assert_called_with(
            msg='No package found.')

    @patch('validations.library.check_package_update._command')
    def test_returns_current_and_available_versions(self, mock_command):
        mock_command.side_effect = [
            [PKG_INSTALLED, ''],
            [PKG_AVAILABLE, ''],
        ]
        check_update(self.module, 'foo-package', 'yum')
        self.module.exit_json.assert_called_with(changed=False,
                                                 name='foo-package',
                                                 current_version='6.1.5',
                                                 latest_minor_version='6.2.0',
                                                 latest_major_version='8.0.0')

    @patch('validations.library.check_package_update._command')
    def test_returns_current_version_if_no_updates(self, mock_command):
        mock_command.side_effect = [
            [PKG_INSTALLED, ''],
            ['', 'No packages found'],
        ]
        check_update(self.module, 'foo-package', 'yum')
        self.module.exit_json.assert_called_with(changed=False,
                                                 name='foo-package',
                                                 current_version='6.1.5',
                                                 latest_minor_version='6.1.5',
                                                 latest_major_version=None)
