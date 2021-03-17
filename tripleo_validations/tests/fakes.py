#   Copyright 2021 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""This sub module provides various data structures and functions
useful for automated testing. Additional helpers should be placed here
if at all possible. This should help with reduction of redundancy and
isolation of potentially problematic testing code.
"""

import sys
try:
    from unittest import mock
except ImportError:
    import mock

sys.modules['uuidutils'] = mock.MagicMock()
sys.modules['xml.etree'] = mock.MagicMock()
sys.modules['glanceclient.exc'] = mock.MagicMock()
sys.modules['ironic_inspector_client'] = mock.MagicMock()
sys.modules['novaclient.exceptions'] = mock.MagicMock()

MOCK_CPUS_RET_VALUE = (
    [0, 1],
    [{'numa_node': 0, 'thread_siblings': [0, 2], 'cpu': 0},
        {'numa_node': 0, 'thread_siblings': [4, 6], 'cpu': 4},
        {'numa_node': 0, 'thread_siblings': [8, 10], 'cpu': 8},
        {'numa_node': 1, 'thread_siblings': [1, 3], 'cpu': 1},
        {'numa_node': 1, 'thread_siblings': [5, 7], 'cpu': 5},
        {'numa_node': 1, 'thread_siblings': [9, 11], 'cpu': 9}
    ])

MOCK_ROLES_INFO = [
    {
        'name': 'foo',
        'flavor': 'bar',
        'count': 9999}]

MOCK_FLAVORS = {
    'ok': {
        'bar': {
            'keys': {
                'resources:fizz': 'fizz',
                'resources:buzz': 'buzz',
                'resources:DISK_GB': 1,
                'MEMORY_MB': 10,
                'VCPU': 100
            }
        }
    },
    'fail_NOVCPU': {
        'bar': {
            'keys': {
                'resources:fizz': 'fizz',
                'resources:buzz': 'buzz',
                'resources:DISK_GB': 1,
                'MEMORY_MB': 10
            }
        }
    }
}

MOCK_FLAVORS_CHECK_EXPECTED = {
    'ok': (
            {'bar': (
                ({'keys': {
                    'resources:fizz': 'fizz',
                    'resources:buzz': 'buzz',
                    'resources:DISK_GB': 1,
                    'MEMORY_MB': 10,
                    'VCPU': 100
                }},
                9999)
            )},
            [],
            [
                'Flavor bar does not have a custom resource class associated with it',
                'Flavor bar has to have scheduling based on standard properties disabled by setting resources:VCPU=0 resources:MEMORY_MB=0 resources:DISK_GB=0 in the flavor property'
            ]
    ),
    'fail_NOVCPU': (
            {'bar': (
                ({'keys': {
                    'resources:fizz': 'fizz',
                    'resources:buzz': 'buzz',
                    'resources:DISK_GB': 1,
                    'MEMORY_MB': 10,
                }},
                9999)
            )},
            [],
            [
                'Flavor bar does not have a custom resource class associated with it',
                'Flavor bar has to have scheduling based on standard properties disabled by setting resources:VCPU=0 resources:MEMORY_MB=0 resources:DISK_GB=0 in the flavor property'
            ]
    )
}


MOCK_NODES = [
    {
        'uuid': 'foo123',
        'provision_state': 'active',
        'properties': {
            'capabilities': {
                'foocap': 'foocapdesc'
            }
        }
    },
    {
        'uuid': 'bar123',
        'provision_state': 'active',
        'properties': {
            'capabilities': {
                'barcap': 'bcapdesc'
            }
        }
    }
]


MOCK_PROFILE_FLAVORS = {
    'fooflavor': (MOCK_FLAVORS['ok'], 1),
}


UUIDs = [
    '13c319a4-7704-4b44-bb2e-501951879f96',
    '8201bb8e-be20-4a97-bcf4-91bcf7eeff86',
    'cc04effd-6bac-45ba-a0dc-83e6cd2c589d',
    'cbb12140-a088-4646-a873-73eeb055ccc2'
]


def node_helper(node_id, kernel_id, ram_id, arch=None, platform=None):

    node = {
        "uuid": node_id,
        "driver_info": {
            "deploy_kernel": kernel_id,
            "deploy_ramdisk": ram_id,
        },
        "properties": {},
        "extra": {},
    }
    if arch:
        node["properties"]["cpu_arch"] = arch
    if platform:
        node["extra"]["tripleo_platform"] = platform
    return node
