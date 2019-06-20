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


import library.check_ironic_boot_config as validation
from tripleo_validations.tests import base

import mock

KERNEL_IMAGE_ID = 111
RAMDISK_IMAGE_ID = 112
KERNEL_NAME_BASE = "bm-deploy-kernel"
RAMDISK_NAME_BASE = "bm-deploy-ramdisk"


class TestCheckIronicBootConfig(base.TestCase):

    def _image_helper(self, prefixes):
        # first set of images gets the magic ID
        yield {
            "id": KERNEL_IMAGE_ID,
            "name": prefixes[0] + KERNEL_NAME_BASE
        }
        yield {
            "id": RAMDISK_IMAGE_ID,
            "name": prefixes[0] + RAMDISK_NAME_BASE
        }
        if len(prefixes) > 1:
            # if there's a second set of images give them some other ID
            yield {
                "id": KERNEL_IMAGE_ID + 2,
                "name": prefixes[1] + KERNEL_NAME_BASE
            }
            yield {
                "id": RAMDISK_IMAGE_ID + 2,
                "name": prefixes[1] + RAMDISK_NAME_BASE
            }

    def _node_helper(self, arch, platform):
        # just create one node
        nodes = [
            {"uuid": 222,
             "driver_info":
                 {
                     "deploy_kernel": KERNEL_IMAGE_ID,  # magic ID
                     "deploy_ramdisk": RAMDISK_IMAGE_ID  # magic ID
                 },
             "properties": {},
             "extra": {},
             }
        ]
        if arch:
            nodes[0]["properties"]["cpu_arch"] = arch
        if platform:
            nodes[0]["extra"]["tripleo_platform"] = platform
        return nodes

    def _do_test_case(
            self, image_prefixes, node_arch=None, node_platform=None):
        images = self._image_helper(image_prefixes)
        nodes = self._node_helper(node_arch, node_platform)
        return validation.validate_boot_config(
            images, nodes, KERNEL_NAME_BASE, RAMDISK_NAME_BASE)

    def test_successes(self):
        self.assertEqual(
            [], self._do_test_case(['p9-ppc64le-'], 'ppc64le', 'p9'))
        self.assertEqual(
            [], self._do_test_case([''], 'ppc64le', 'p9'))
        self.assertEqual(
            [], self._do_test_case(
                ['ppc64le-', 'p8-ppc64le-'], 'ppc64le', 'p9'))
        self.assertEqual(
            [], self._do_test_case(
                ['', 'SB-x86_64-'], 'ppc64le', 'p9'))
        self.assertEqual(
            [], self._do_test_case([''], 'x86_64'))
        self.assertEqual(
            [], self._do_test_case(['']))

    @mock.patch('library.check_ironic_boot_config.NO_CANDIDATES')
    @mock.patch('library.check_ironic_boot_config.MISMATCH')
    def test_errors(self, mismatch, no_candidates):
        self._do_test_case(['p8-ppc64le-', 'p9-ppc64le-'], 'ppc64le', 'p9')
        mismatch.format.assert_called()
        no_candidates.format.assert_not_called()

        mismatch.reset_mock()
        no_candidates.reset_mock()

        self._do_test_case(['ppc64le-', 'p9-ppc64le-'], 'ppc64le', 'p9')
        mismatch.format.assert_called()
        no_candidates.format.assert_not_called()

        mismatch.reset_mock()
        no_candidates.reset_mock()

        self._do_test_case(['', 'ppc64le-'], 'ppc64le')
        mismatch.format.assert_called()
        no_candidates.format.assert_not_called()

        mismatch.reset_mock()
        no_candidates.reset_mock()

        self._do_test_case(['p9-ppc64le-', ''], 'ppc64le')
        mismatch.format.assert_called()
        no_candidates.format.assert_not_called()

        mismatch.reset_mock()
        no_candidates.reset_mock()

        self._do_test_case(['p8-ppc64le-'], 'ppc64le', 'p9')
        mismatch.format.assert_not_called()
        no_candidates.format.assert_called()

        mismatch.reset_mock()
        no_candidates.reset_mock()

        self._do_test_case(['p9-ppc64le-', 'x86_64-'], 'ppc64le')
        mismatch.format.assert_not_called()
        no_candidates.format.assert_called()
