# Copyright 2019 Red Hat, Inc.
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

"""Tests of the check_ironic_boot_config submodule.
The initial try/except block is a safeguard against Python version
incompatibility and general confusion it can cause.
But worry not, it's barely used these days.
"""
try:
    from unittest import mock
except ImportError:
    import mock

import tripleo_validations.tests.base as base
import tripleo_validations.tests.fakes as fakes
import library.check_ironic_boot_config as validation


class TestCheckIronicBootConfigModule(base.TestCase):

    def setUp(self):
        super(TestCheckIronicBootConfigModule, self).setUp()
        self.module = validation

    def test_module_init(self):
        module_attributes = dir(self.module)

        required_attributes = [
            'DOCUMENTATION',
            'EXAMPLES'
        ]

        self.assertTrue(set(required_attributes).issubset(module_attributes))

    @mock.patch(
        'library.check_ironic_boot_config.yaml_safe_load',
        return_value={'options': 'fizz'})
    @mock.patch(
        'library.check_ironic_boot_config.validate_boot_config',
        return_value=None)
    @mock.patch('library.check_ironic_boot_config.AnsibleModule')
    def test_module_main_success(self, mock_module,
                                 mock_validate_boot_config,
                                 mock_yaml_safe_load):

        module_calls = [
            mock.call(argument_spec='fizz'),
            mock.call().params.get('nodes'),
            mock.call().exit_json()
        ]

        self.module.main()

        mock_validate_boot_config.assert_called_once()
        mock_module.assert_has_calls(module_calls)

    @mock.patch(
        'library.check_ironic_boot_config.yaml_safe_load',
        return_value={'options': 'fizz'})
    @mock.patch(
        'library.check_ironic_boot_config.validate_boot_config',
        return_value=['foo', 'bar'])
    @mock.patch('library.check_ironic_boot_config.AnsibleModule')
    def test_module_main_fail(self, mock_module,
                              mock_validate_boot_config,
                              mock_yaml_safe_load):

        module_calls = [
            mock.call(argument_spec='fizz'),
            mock.call().params.get('nodes'),
            mock.call().fail_json('foobar')
        ]

        self.module.main()

        mock_validate_boot_config.assert_called_once()
        mock_module.assert_has_calls(module_calls)

    def test_too_diverse(self):
        """Test if the function returns string without raising exception.
        """

        return_value = self.module._too_diverse(
            'foo',
            [
                'bar',
                'fizz',
                'buzz'
            ],
            '000')

        self.assertIsInstance(return_value, str)

    def test_invalid_image_entry(self):
        """Test if the function returns string without raising exception.
        """

        return_value = self.module._invalid_image_entry(
            'foo',
            [
                'bar',
                'fizz',
                'buzz'
            ],
            '000')

        self.assertIsInstance(return_value, str)


class TestValidateBootConfig(base.TestCase):
    """Tests for validate_boot_config function of the check_ironic_boot_config
    submodule. Tests assert on returned value and calls made.
    """

    @mock.patch('library.check_ironic_boot_config._too_diverse')
    @mock.patch('library.check_ironic_boot_config._invalid_image_entry')
    def test_validate_boot_config_success(self, mock_image_entry_error, mock_diverse_error):
        """As we are trying to verify functionality for multiple subsets
        of various nodes, this test is slightly more complex.
        List of nodes is sliced and individual slices are fed
        to the validate_boot_config function we are testing.
        However, this approach still doesn't test all the possibilities.
        For example the order of original list is maintained, and number
        of nodes is very, very limited.
        Further improvement will require consultation.
        """
        nodes = [
            fakes.node_helper(1, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(2, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(3, 'file://k.img', 'file://r.img', 'ppc64le', 'p9'),
            fakes.node_helper(4, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le')
        ]

        for node_slice in [nodes[::index] for index in range(1, len(nodes))]:
            errors = validation.validate_boot_config(node_slice)

            mock_diverse_error.assert_not_called()
            mock_image_entry_error.assert_not_called()

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 0)

    @mock.patch('library.check_ironic_boot_config._too_diverse')
    def test_validate_boot_config_fail_too_diverse_uuid(self, mock_error):
        nodes = [
            fakes.node_helper(1, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(2, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(3, 'file://k.img', 'file://r.img', 'ppc64le', 'p9'),
            fakes.node_helper(4, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le'),
            fakes.node_helper(5, fakes.UUIDs[2], fakes.UUIDs[3], 'ppc64le', 'p9'),
        ]

        validation.validate_boot_config(nodes)
        mock_error.assert_called()

    @mock.patch('library.check_ironic_boot_config._too_diverse')
    def test_validate_boot_config_fail_too_diverse_path(self, mock_error):
        nodes = [
            fakes.node_helper(1, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(2, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(3, 'file://k.img', 'file://r.img', 'ppc64le', 'p9'),
            fakes.node_helper(4, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le'),
            fakes.node_helper(5, 'file://k2.img', 'file://r2.img', 'ppc64le', 'p9')
        ]

        calls = [
            mock.call('file-based', ('kernel', 'ppc64le', 'p9'), {'file://k.img', 'file://k2.img'}),
            mock.call('file-based', ('ramdisk', 'ppc64le', 'p9'), {'file://r2.img', 'file://r.img'})
        ]

        validation.validate_boot_config(nodes)
        mock_error.assert_has_calls(calls)

    @mock.patch('library.check_ironic_boot_config._invalid_image_entry')
    def test_validate_boot_config_fail_invalid_image_entry(self, mock_error):
        nodes = [
            fakes.node_helper(1, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(2, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le', 'p9'),
            fakes.node_helper(3, 'file://k.img', 'file://r.img', 'ppc64le', 'p9'),
            fakes.node_helper(4, fakes.UUIDs[0], fakes.UUIDs[1], 'ppc64le'),
            fakes.node_helper(5, 'not_uuid_or_path', 'not_uuid_or_path')
        ]

        calls = [
            mock.call('kernel', 'not_uuid_or_path', 5),
            mock.call('ramdisk', 'not_uuid_or_path', 5)
        ]

        validation.validate_boot_config(nodes)

        mock_error.assert_has_calls(calls)
