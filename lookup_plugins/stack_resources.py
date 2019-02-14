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


from ansible.plugins.lookup import LookupBase


from tripleo_validations import utils


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns the current plan's stack resources.

        :return: A list of dicts
        """
        ret = []
        heat = utils.get_heat_client(variables)
        resource_list = heat.resources.list(variables['plan'])
        for resource in resource_list:
            ret.append(dict(
                resource_name=resource.resource_name,
                resource_status=resource.resource_status,
                logical_resource_id=resource.logical_resource_id,
                links=resource.links,
                creation_time=resource.creation_time,
                resource_status_reason=resource.resource_status_reason,
                updated_time=resource.updated_time,
                required_by=resource.required_by,
                physical_resource_id=resource.physical_resource_id,
                resource_type=resource.resource_type
                ))
        return ret
