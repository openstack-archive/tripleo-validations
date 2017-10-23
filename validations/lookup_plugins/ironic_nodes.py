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
    lookup: ironic_nodes
    description: Retrieve node information from Ironic
    long_description:
      - Load node information using the Ironic API
    options:
      _terms:
        description: Optional filter attribute and filter value
    author: Florian Fuchs <flfuchs@redhat.com>
"""

EXAMPLES = """
    - name: Get all nodes from Ironic
      debug:
        msg: "{{ lookup('ironic_nodes', wantlist=True) }}"

    - name: Lookup all nodes that match a list of IDs
      debug:
        msg: |
             {{ lookup('ironic_nodes', 'id',
             ['c8a1c7b8-d6b1-408b-b4a6-5881efdfd65c',
             '4bea536d-9d37-432f-a77e-7c65f1cf3acb'],
             wantlist=True) }}"

    - name: Get all nodes for a set of instance UUIDs
      debug:
        msg: |
             {{ lookup(''ironic_nodes', 'instance_uuid',
             ['1691a1c7-9974-4bcc-a07a-5dec7fc04da0',
             '07f2435d-820c-46ce-9097-cf8a7282293e'],
             wantlist=True) }}"
"""

RETURN = """
_raw:
    description: A Python list with results from the API call.
"""

from ansible.plugins.lookup import LookupBase
from ironicclient import client as ironic_client
from six import string_types

from tripleo_validations.utils import get_auth_session


def filtered(node):
    # For each node only return properties whose value
    # can be properly serialized.
    return {k: v for k, v in node.__dict__.items()
            if isinstance(v, (string_types, int, list, dict, type(None)))}


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns node information from ironic."""
        auth_url = variables.get('auth_url')
        username = variables.get('username')
        project_name = variables.get('project_name')
        token = variables.get('os_auth_token')
        session = get_auth_session(auth_url, username, project_name,
                                   auth_token=token)
        ironic_url = session.get_endpoint(service_type='baremetal',
                                          interface='public')
        ironic = ironic_client.get_client(1, ironic_url=ironic_url,
                                          os_auth_token=token)

        if len(terms) > 0:
            if terms[0] == 'id':
                nodes = [ironic.node.get(id) for id in terms[1]]
                return [filtered(node) for node in nodes]
            elif terms[0] == 'instance_uuid':
                nodes = [ironic.node.get_by_instance_uuid(uuid)
                         for uuid in terms[1]]
                return [filtered(node) for node in nodes]
        else:
            return [filtered(node)
                    for node in ironic.node.list(detail=True)]
