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
test_ceph_pools_pg_protection
-----------------------------

Tests for `ceph_pools_pg_protection` module.
"""

import library.ceph_pools_pg_protection as validation
from tripleo_validations.tests import base


class TestCephPoolsPgProtection(base.TestCase):

    def test_check_pg_num_enough_osds(self):
        '''Test adding one more pool to the existing pools with 36 OSDs'''
        num_osds = 36
        pools = {'images': {'pg_num': 128, 'size': 3},
                 'vms': {'pg_num': 256, 'size': 3},
                 'volumes': {'pg_num': 512, 'size': 3}}
        msg = validation.check_pg_num('backups', 128, 3, num_osds, 200, pools)
        self.assertEqual(msg, "")

    def test_check_pg_num_not_enough_osds(self):
        '''Test adding one more pool to the existing pools with 1 OSD'''
        num_osds = 1
        error = "Cannot add pool: backups pg_num 128 size 3 "
        error += "would mean 2688 total pgs, which exceeds max 200 "
        error += "(mon_max_pg_per_osd 200 * num_in_osds 1)"
        pools = {'images': {'pg_num': 128, 'size': 3},
                 'vms': {'pg_num': 256, 'size': 3},
                 'volumes': {'pg_num': 512, 'size': 3}}
        msg = validation.check_pg_num('backups', 128, 3, num_osds, 200, pools)
        self.assertEqual(msg, error)

    def test_simulate_pool_creation_enough_osds(self):
        '''Test creating 3 pools with differing PGs with 36 OSDs'''
        num_osds = 36
        pools = [{'name': 'images', 'pg_num': 128, 'size': 3},
                 {'name': 'vms', 'pg_num': 256, 'size': 3},
                 {'name': 'volumes', 'pg_num': 512, 'size': 3}]
        sim = validation.simulate_pool_creation(num_osds, pools)
        self.assertEqual(sim['failed'], False)
        self.assertEqual(sim['msg'], "")

    def test_simulate_pool_creation_not_enough_osds(self):
        '''Test creating 3 pools with differing PGs with 1 OSD'''
        num_osds = 1
        pools = [{'name': 'images', 'pg_num': 128, 'size': 3},
                 {'name': 'vms', 'pg_num': 256, 'size': 3},
                 {'name': 'volumes', 'pg_num': 512, 'size': 3}]
        sim = validation.simulate_pool_creation(num_osds, pools)
        self.assertEqual(sim['failed'], True)

        error_head = "The following Ceph pools would be created (but no others):\n"
        order0 = "{'images': {'size': 3}, 'pg_num': 128}\n"
        order1 = "{'images': {'pg_num': 128, 'size': 3}}\n"
        error_tail = "Pool creation would then fail with the following from Ceph:\n"
        error_tail += "Cannot add pool: vms pg_num 256 size 3 would mean 384 total pgs, "
        error_tail += "which exceeds max 200 (mon_max_pg_per_osd 200 * num_in_osds 1)\n"
        error_tail += "Please use https://ceph.io/pgcalc and then update the "
        error_tail += "CephPools parameter"

        self.assertTrue(
            (sim['msg'] == error_head + order0 + error_tail)
            or (sim['msg'] == error_head + order1 + error_tail))
