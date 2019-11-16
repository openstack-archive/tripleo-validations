#!/usr/bin/env python
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

from yaml import safe_load as yaml_safe_load
from ansible.module_utils.basic import AnsibleModule


ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ceph_pools_pg_protection
short_description: Warn if Ceph will not create CephPools based on PG and OSD numbers
description:
    - "The Ceph PG overdose protection check (https://ceph.com/community/new-luminous-pg-overdose-protection) is executed by Ceph before a pool is created. If the check does not pass, then the pool is not created. When TripleO deploys Ceph it triggers ceph-ansible which creates the pools that OpenStack needs. This validation runs the same check that the overdose protection uses to determine if the user should update their CephPools, PG count, or number of OSDs. Without this check a deployer may have to wait until after Ceph is running but before the pools are created to realize the deployment will fail."
options:
    num_osds:
        description:
            - The number of Ceph OSDs expected to be running during Pool creation.
            - TripleO does not have this parameter
            - In theory you can derive this parameter from TripleO parameters
        required: True
        type: int
    ceph_pool_default_size:
        description:
            - The same as the TripleO CephPoolDefaultSize parameter
            - Number of replicas of the data
        required: False
        default: 3
        type: int
    ceph_pool_default_pg_num:
        description:
            - The same as the TripleO CephPoolDefaultPgNum parameter
            - The default number of Placement Groups a pool should have
            - Ceph defaults this number to 16
            - TripleO defaults this number to 128
        required: False
        default: 128
        type: int
    ceph_pools:
        description:
            - The same as the TripleO CephPools parameter
            - A list of dictionaries
            - Each embedded dict must have a name parameter
            - Optional pg_num and size parameters may be set per pool
        required: True
        type: list
author:
    - John Fulton (fultonj)
'''

EXAMPLES = '''
# Call this module from TripleO Ansible Validations

- name: Is the CephPools parameter configured correctly?
  ceph_pools_pg_protection:
    num_osds: 36
    ceph_pool_default_size: 3
    ceph_pool_default_pg_num: 128
    ceph_pools:
      - {"name": volumes,  "pg_num": 1024,"pgp_num": 1024, "application": rbd, "size": 3}
      - {"name": vms,      "pg_num": 512, "pgp_num": 512, "application": rbd, "size": 3}
      - {"name": images,   "pg_num": 128, "pgp_num": 128, "application": rbd, "size": 3}
    register: pool_creation_simulation
- name: Fail if CephPools parameter is not configured correctly
  fail:
    msg: pool_creation_simulation["message"]
  when: not pool_creation_simulation["valid_input"]

# Call this module from within TripleO Heat Templates (if only num_osds was derived)
- name: Is the CephPools parameter configured correctly?
  ceph_pools_pg_protection:
    num_osds: 36
    ceph_pool_default_size: {get_param: CephPoolDefaultSize}
    ceph_pool_default_pg_num: {get_param: CephPoolDefaultPgNum}
    ceph_pools: {get_param: CephPools}
    register: pool_creation_simulation

'''

RETURN = '''
message:
    description: A description of why Ceph might refuse to create the requested CephPools
    type: str
    returned: always
valid_input:
    description: True only if Ceph would create all requested pools
    type: boolean
    returned: always
'''


def check_pg_num(pool, pg_num, size, num_osds=0, max_pgs_per_osd=200, pools={}):
    """
    Returns empty string only if the Pool PG numbers are correct for the OSDs.
    Otherwise returns an error message like the one Ceph would return.
    """
    # The original check in C++ from the Ceph source code is:
    #
    # int OSDMonitor::check_pg_num(int64_t pool, int pg_num, int size, ostream *ss)
    # {
    #   auto max_pgs_per_osd = g_conf->get_val<uint64_t>("mon_max_pg_per_osd");
    #   auto num_osds = std::max(osdmap.get_num_in_osds(), 3u); // assume min cluster size 3
    #   auto max_pgs = max_pgs_per_osd * num_osds;
    #   uint64_t projected = 0;
    #   if (pool < 0) {
    #     projected += pg_num * size;
    #   }
    #   for (const auto& i : osdmap.get_pools()) {
    #     if (i.first == pool) {
    #       projected += pg_num * size;
    #     } else {
    #       projected += i.second.get_pg_num() * i.second.get_size();
    #     }
    #   }
    #   if (projected > max_pgs) {
    #     if (pool >= 0) {
    #       *ss << "pool id " << pool;
    #     }
    #     *ss << " pg_num " << pg_num << " size " << size
    # 	<< " would mean " << projected
    # 	<< " total pgs, which exceeds max " << max_pgs
    # 	<< " (mon_max_pg_per_osd " << max_pgs_per_osd
    # 	<< " * num_in_osds " << num_osds << ")";
    #     return -ERANGE;
    #   }
    #   return 0;
    # }
    import six
    msg = ""
    max_pgs = max_pgs_per_osd * num_osds
    projected = 0
    if len(pool) < 0:
        projected = projected + (pg_num * size)
    for pool_name, pool_sizes in six.iteritems(pools):
        if pool_name == pool:
            projected = projected + (pg_num * size)
        else:
            projected = projected + (int(pool_sizes['pg_num']) * int(pool_sizes['size']))
    if projected > max_pgs:
        msg = "Cannot add pool: " + str(pool) + \
              " pg_num " + str(pg_num) + " size " + str(size) + \
              " would mean " + str(projected) + \
              " total pgs, which exceeds max " + str(max_pgs) + \
              " (mon_max_pg_per_osd " + str(max_pgs_per_osd) + \
              " * num_in_osds " + str(num_osds) + ")"
    return msg


def simulate_pool_creation(num_osds, ceph_pools,
                           ceph_pool_default_size=3,
                           ceph_pool_default_pg_num=128,
                           max_pgs_per_osd=200):
    """
    Simulate ceph-ansible asking Ceph to create the pools in the ceph_pools list
    """
    msg = ""
    failed = False
    created_pools = {}
    for pool in ceph_pools:
        if 'size' not in pool:
            pool['size'] = ceph_pool_default_size
        if 'pg_num' not in pool:
            pool['pg_num'] = ceph_pool_default_pg_num
        ceph_msg = check_pg_num(pool['name'], pool['pg_num'], pool['size'],
                                num_osds, max_pgs_per_osd, created_pools)
        if len(ceph_msg) == 0:
            created_pools[pool['name']] = {'pg_num': pool['pg_num'], 'size': pool['size']}
        else:
            failed = True
            break
    if failed:
        msg = "The following Ceph pools would be created (but no others):" + \
              "\n" + str(created_pools) + "\n" + \
              "Pool creation would then fail with the following from Ceph:" + \
              "\n" + ceph_msg + "\n" + \
              "Please use https://ceph.io/pgcalc and then update the CephPools parameter"
    simulation_results = {}
    simulation_results['failed'] = failed
    simulation_results['msg'] = msg
    return simulation_results


def run_module():
    # Seed the result dict in the object
    result = dict(
        changed=False,
        valid_input=True,
        message=''
    )

    # Use AnsibleModule object abstraction to work with Ansible
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options'],
        supports_check_mode=False
    )

    # Check mode not supported
    if module.check_mode:
        module.exit_json(**result)

    # Simulate Ceph pool creation
    simulation = simulate_pool_creation(module.params['num_osds'],
                                        module.params['ceph_pools'],
                                        module.params['ceph_pool_default_size'],
                                        module.params['ceph_pool_default_pg_num'])
    if simulation['failed']:
        result['message'] = "Invalid Ceph configuration: " + simulation['msg']
        result['valid_input'] = False
    else:
        result['message'] = 'Provided CephPools satisfy PG overdose protection'
        result['valid_input'] = True

    # This module never changes state of a target system, it only
    # evaluates if inputs will work when Ceph processes then.
    # There shouldn't be anything like the following
    # result['changed'] = True

    # This module does not currently have fail options. It should
    # only evaluate input and make result of the evaluation available.
    # So it doesn't currently do anything like the following by design.
    # module.fail_json(msg='Failing for invalid input', **result)

    # Exit and pass the key/value results of the simulation
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
