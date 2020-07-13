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

try:
    from unittest import mock
except ImportError:
    import mock

import library.check_ironic_boot_config as validation
from tripleo_validations.tests import base

UUIDs = [
    '13c319a4-7704-4b44-bb2e-501951879f96',
    '8201bb8e-be20-4a97-bcf4-91bcf7eeff86',
    'cc04effd-6bac-45ba-a0dc-83e6cd2c589d',
    'cbb12140-a088-4646-a873-73eeb055ccc2'
]


class TestCheckIronicBootConfig(base.TestCase):

    def _node_helper(self, n_id, k_id, r_id, arch=None, platform=None):
        node = {
            "uuid": n_id,
            "driver_info": {
                "deploy_kernel": k_id,
                "deploy_ramdisk": r_id,
            },
            "properties": {},
            "extra": {},
        }
        if arch:
            node["properties"]["cpu_arch"] = arch
        if platform:
            node["extra"]["tripleo_platform"] = platform
        return node

    def _do_positive_test_case(self, nodes):
        res = validation.validate_boot_config(nodes)
        self.assertEqual([], res)

    def _do_negative_test_case(self, nodes, fail_reason='too_diverse'):
        with mock.patch(
                'library.check_ironic_boot_config._%s' % fail_reason) as e:
            validation.validate_boot_config(nodes)
            e.assert_called()

    def test_basic_functionality(self):
        nodes = [
            self._node_helper(1, UUIDs[0], UUIDs[1], 'ppc64le', 'p9'),
            self._node_helper(2, UUIDs[0], UUIDs[1], 'ppc64le', 'p9')
        ]
        self._do_positive_test_case(nodes)

        nodes.append(
            self._node_helper(
                3, 'file://k.img', 'file://r.img', 'ppc64le', 'p9')
        )
        self._do_positive_test_case(nodes)

        nodes.append(
            self._node_helper(4, UUIDs[0], UUIDs[1], 'ppc64le')
        )
        self._do_positive_test_case(nodes)

        nodes.append(
            self._node_helper(5, UUIDs[2], UUIDs[3], 'ppc64le', 'p9'),
        )
        self._do_negative_test_case(nodes)
        nodes = nodes[:-1]

        nodes.append(
            self._node_helper(
                5, 'file://k2.img', 'file://r2.img', 'ppc64le', 'p9')
        )
        self._do_negative_test_case(nodes)
        nodes = nodes[:-1]

        nodes.append(
            self._node_helper(5, 'not_uuid_or_path', 'not_uuid_or_path')
        )
        self._do_negative_test_case(nodes, 'invalid_image_entry')
