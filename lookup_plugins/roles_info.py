#!/usr/bin/env python

# Copyright 2017 Red Hat, Inc.
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

import yaml

from ansible.plugins.lookup import LookupBase

from tripleo_validations import utils


DOCUMENTATION = """
    lookup: roles_info
    description: Retrieve role information from Heat and Swift.
    long_description:
      - Load role information using the Heat API.
    options:
      _terms:
        description: Optional filter attribute and filter value
    author: Brad P. Crochet <brad@redhat.com>
"""

EXAMPLES = """
    - name: Get all role info from Heat and Swift
      debug:
        msg: |
             {{ lookup('roles_info', wantlist=True) }}

"""

RETURN = """
_raw:
    description: A Python list with results from the API call.
"""


class LookupModule(LookupBase):
    def _get_object_yaml(self, swiftclient, container, obj):
        obj_ret = swiftclient.get_object(container=container, obj=obj)
        return yaml.safe_load(obj_ret[1])

    def run(self, terms, variables=None, **kwargs):
        """Returns server information from nova."""
        swift = utils.get_swift_client(variables)
        plan = variables.get('plan')
        plan_env = self._get_object_yaml(swift, plan, 'plan-environment.yaml')
        roles_data = self._get_object_yaml(swift, plan, 'roles_data.yaml')

        def default_role_data(role):
            return {
                'name': role['name'],
                'count': role.get('CountDefault', 0),
                'flavor': role.get('FlavorDefault', 'baremetal')
            }

        roles = list(map(default_role_data, roles_data))

        parameter_defaults = plan_env.get('parameter_defaults', {})

        for role in roles:
            new_count = parameter_defaults.get("%sCount" % role['name'])
            if new_count:
                role['count'] = new_count

            new_flavor = parameter_defaults.get("Overcloud%sFlavor" %
                                                role['name'])
            if new_flavor:
                role['flavor'] = new_flavor

        return roles
