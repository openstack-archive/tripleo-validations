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
from ironic_inspector_client import ClientError
from ironic_inspector_client import ClientV1
from ironicclient import client

from tripleo_validations.utils import get_auth_session


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns Ironic Inspector introspection data.

        Access swift and return introspection data for all nodes.

        :returns a list of tuples, one for each node.
        """

        session = get_auth_session({
            'auth_url': kwargs.get('auth_url'),
            'password': kwargs.get('password'),
            'username': 'ironic',
            'project_name': 'service',
            })
        ironic = client.get_client(1, session=session)
        ironic_inspector = ClientV1(session=session)

        ret = []
        for node in ironic.node.list():
            try:
                ret.append((node.name, ironic_inspector.get_data(node.uuid)))
            except ClientError:
                pass

        return ret
