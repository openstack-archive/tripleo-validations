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

from tripleo_validations.tests import base

from validations.library.node_disks import _get_smallest_disk
from validations.library.node_disks import _has_root_device_hints
from validations.library.node_disks import validate_node_disks


# node_1: 2 disks, 1 larger than 4GB (50GB)
# node_2: 3 disks, 2 larger than 4GB (50GB, 10GB)
# node_2: 3 disks, 2 larger than 4GB (50GB, 10GB)
INTROSPECTION_DATA = {
    'node_1': {
        "inventory": {
            "disks": [
                {"name": "disk-1", "size": 53687091200},
                {"name": "disk-2", "size": 4294967296},
            ]
        }
    },
    'node_2': {
        "inventory": {
            "disks": [
                {"name": "disk-1", "size": 53687091200},
                {"name": "disk-2", "size": 10737418240},
                {"name": "disk-3", "size": 4294967296},
            ]
        }
    },
    'node_3': {
        "inventory": {
            "disks": [
                {"name": "disk-1", "size": 53687091200},
                {"name": "disk-2", "size": 10737418240},
                {"name": "disk-3", "size": 4294967296},
            ]
        }
    },
}

# small: fits nodes with disks >= 10GB
# large: fits nodes with disks >= 50GB
FLAVOR_DATA = {
    "small": {
        "disk": 10,
        "name": "small"
    },
    "large": {
        "disk": 50,
        "name": "large"
    },
}

# node_1: no root device set, one disk > 4GB, fits both flavors
# node_2: root device set to name of disk-2 which fits both flavors
# node_3: no root device set, small disk only fits small flavor
NODE_DATA = {
    "node_1": {"properties": {}},
    "node_2": {
        "properties": {
            "root_device": {
                "wwn": "0x4000cca77fc4dba1"
            }
        }
    },
    "node_3": {"properties": {}},
}


class TestGetSmallestDisk(base.TestCase):

    def test_get_correct_disk(self):
        introspection_data = INTROSPECTION_DATA['node_2']
        smallest_disk = _get_smallest_disk(
            introspection_data['inventory']['disks'])
        self.assertEqual(smallest_disk['size'], 4294967296)


class TestHasRootDeviceHints(base.TestCase):

    def test_detect_root_device_hints(self):
        self.assertTrue(_has_root_device_hints('node_2', NODE_DATA))

    def test_detect_no_root_device_hints(self):
        self.assertFalse(_has_root_device_hints('node_1', NODE_DATA))


class TestValidateRootDeviceHints(base.TestCase):

    def setUp(self):
        super(TestValidateRootDeviceHints, self).setUp()

    def test_node_1_no_warning(self):
        introspection_data = {
            'node_1': INTROSPECTION_DATA['node_1']
        }
        errors, warnings = validate_node_disks({},
                                               FLAVOR_DATA,
                                               introspection_data)
        self.assertEqual([[], []], [errors, warnings])

    def test_small_flavor_no_hints_warning(self):
        introspection_data = {
            'node_2': INTROSPECTION_DATA['node_2']
        }
        flavors = {
            "small": FLAVOR_DATA['small']
        }
        expected_warnings = [
            'node_2 has more than one disk available for deployment',
        ]
        errors, warnings = validate_node_disks({},
                                               flavors,
                                               introspection_data)
        self.assertEqual([[], expected_warnings], [errors, warnings])

    def test_large_flavor_no_hints_error(self):
        introspection_data = {
            'node_3': INTROSPECTION_DATA['node_3']
        }
        expected_errors = [
            'node_3 has more than one disk available for deployment and no '
            'root device hints set. The disk that will be used is too small '
            'for the flavor with the largest disk requirement ("large").',
        ]
        errors, warnings = validate_node_disks({},
                                               FLAVOR_DATA,
                                               introspection_data)
        self.assertEqual([expected_errors, []], [errors, warnings])
