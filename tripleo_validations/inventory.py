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

from heatclient.exc import HTTPNotFound

HOST_NETWORK = 'ctlplane'


class StackOutputs(object):
    """Item getter for stack outputs.

    Some stack outputs take a while to return via the API. This class
    makes sure all outputs of a stack are fully recognized, while only
    calling `stack.output_get` for the ones we're really using.
    """

    def __init__(self, plan, hclient):
        self.plan = plan
        self.outputs = {}
        self.hclient = hclient
        try:
            self.output_list = [
                output['output_key'] for output in
                self.hclient.stacks.output_list(plan)['outputs']]
        except HTTPNotFound:
            self.output_list = []

    def __getitem__(self, key):
        if key not in self.output_list:
            raise KeyError(key)
        if key not in self.outputs:
            self.outputs[key] = self.hclient.stacks.output_show(
                self.plan, key)['output']['output_value']
        return self.outputs[key]

    def __iter__(self):
        return iter(self.output_list)

    def get(self, key, default=None):
        try:
            self.__getitem__(key)
        except KeyError:
            pass
        return self.outputs.get(key, default)


class TripleoInventory(object):
    def __init__(self, configs, session, hclient):
        self.configs = configs
        self.session = session
        self.hclient = hclient
        self.stack_outputs = StackOutputs(self.configs.plan, self.hclient)

    @staticmethod
    def get_roles_by_service(enabled_services):
        # Flatten the lists of services for each role into a set
        services = set(
            [item for role_services in enabled_services.values()
             for item in role_services])

        roles_by_services = {}
        for service in services:
            roles_by_services[service] = []
            for role, val in enabled_services.items():
                if service in val:
                    roles_by_services[service].append(role)
            roles_by_services[service] = sorted(roles_by_services[service])
        return roles_by_services

    def get_overcloud_environment(self):
        try:
            environment = self.hclient.stacks.environment(self.configs.plan)
            return environment
        except HTTPNotFound:
            return {}

    def list(self):
        ret = {
            'undercloud': {
                'hosts': ['localhost'],
                'vars': {
                    'ansible_connection': 'local',
                    'os_auth_token': self.session.get_token(),
                    'plan': self.configs.plan,
                },
            }
        }

        swift_url = self.session.get_endpoint(service_type='object-store',
                                              interface='public')
        if swift_url:
            ret['undercloud']['vars']['undercloud_swift_url'] = swift_url

        keystone_url = self.stack_outputs.get('KeystoneURL')
        if keystone_url:
            ret['undercloud']['vars']['overcloud_keystone_url'] = keystone_url
        admin_password = self.get_overcloud_environment().get(
            'parameter_defaults', {}).get('AdminPassword')
        if admin_password:
            ret['undercloud']['vars']['overcloud_admin_password'] =\
                admin_password
        endpoint_map = self.stack_outputs.get('EndpointMap')
        if endpoint_map:
            horizon_endpoint = endpoint_map.get('HorizonPublic', {}).get('uri')
            if horizon_endpoint:
                ret['undercloud']['vars']['overcloud_horizon_url'] =\
                    horizon_endpoint

        role_net_ip_map = self.stack_outputs.get('RoleNetIpMap', {})
        role_net_hostname_map = self.stack_outputs.get(
            'RoleNetHostnameMap', {})
        children = []
        for role, hostnames in role_net_hostname_map.items():
            if hostnames:
                names = hostnames.get(HOST_NETWORK) or []
                shortnames = [n.split(".%s." % HOST_NETWORK)[0] for n in names]
                children.append(role.lower())
                ret[role.lower()] = {
                    'children': sorted(shortnames),
                    'vars': {
                        'ansible_ssh_user': 'heat-admin',
                    }
                }
                # Create a group per hostname to map hostname to IP
                ips = role_net_ip_map[role][HOST_NETWORK]
                for idx, name in enumerate(shortnames):
                    ret[name] = {'hosts': [ips[idx]]}

        if children:
            ret['overcloud'] = {
                'children': sorted(children)
            }

        # Associate services with roles
        roles_by_service = self.get_roles_by_service(
            self.stack_outputs.get('EnabledServices', {}))
        for service, roles in roles_by_service.items():
            service_children = [role.lower() for role in roles
                                if ret.get(role.lower()) is not None]
            if service_children:
                ret[service.lower()] = {
                    'children': service_children,
                    'vars': {
                        'ansible_ssh_user': 'heat-admin'
                    }
                }

        return ret

    def host(self):
        # NOTE(mandre)
        # Dynamic inventory scripts must return empty json if they don't
        # provide detailed info for hosts:
        # http://docs.ansible.com/ansible/developing_inventory.html
        return {}
