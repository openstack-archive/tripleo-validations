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

DOCUMENTATION = """
    lookup: nova_servers
    description: Retrieve server information from Nova
    long_description:
      - Load server information using the Nova API and search by attribute.
    options:
      _terms:
        description: Optional filter attribute and filter value
    author: Florian Fuchs <flfuchs@redhat.com>
"""

EXAMPLES = """
    - name: Get all server ids from nova
      debug:
        msg: |
             {{ lookup('nova_servers', wantlist=True) |
             map(attribute='id') | join(', ') }}

    - name: Lookup all server ids from nova with a certain ctlplane IP
      debug:
        msg: |
             {{ lookup('nova_servers', 'ip', 'ctlplane', ['192.168.24.15'],
             wantlist=True) | map(attribute='id') | join(', ') }}"

    - name: Get server with name 'overcloud-controller-0'
      debug:
        msg: |
             {{ lookup('nova_servers', 'name', ['overcloud-controller-0'],
             wantlist=True) | map(attribute='name') }}"
"""

RETURN = """
_raw:
    description: A Python list with results from the API call.
"""

from ansible.plugins.lookup import LookupBase
from novaclient import client as nova_client
from novaclient.exceptions import NotFound
from six import string_types

from tripleo_validations.utils import get_auth_session


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns server information from nova."""
        auth_url = variables.get('auth_url')
        username = variables.get('username')
        project_name = variables.get('project_name')
        token = variables.get('os_auth_token')
        session = get_auth_session(auth_url, username, project_name,
                                   auth_token=token)
        nova = nova_client.Client(2, session=session)

        servers = []
        if len(terms) > 0:
            # Look up servers by network and IP
            if terms[0] == 'ip':
                for ip in terms[2]:
                    try:
                        servers.append(nova.servers.find(
                            networks={terms[1]: [ip]}))
                    except NotFound:
                        pass
            # Look up servers by attribute
            else:
                for value in terms[1]:
                    try:
                        search_data = {terms[0]: value}
                        servers.append(nova.servers.find(**search_data))
                    except NotFound:
                        pass
        else:
            servers = nova.servers.list()

        # For each server only return properties whose value
        # can be properly serialized. (Things like
        # novaclient.v2.servers.ServerManager will make
        # Ansible return the whole result as a string.)
        return [{k: v for k, v in server.__dict__.items()
                 if isinstance(v, (string_types, int, list, dict, type(None)))}
                for server in servers]
