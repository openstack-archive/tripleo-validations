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

from swiftclient.client import Connection
from tripleo_validations.utils import get_auth_session


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns Ironic Inspector introspection data.

        Access swift and return introspection data for all nodes.

        :returns a list of tuples, one for each node.
        """
        ret = []

        session = get_auth_session(kwargs.get('auth_url'),
                                   "ironic",
                                   "service",
                                   kwargs.get('password'))

        swift_client = Connection(session=session)
        container = swift_client.get_container("ironic-inspector")

        for item in container[1]:
            if item['name'].startswith('inspector_data') and \
                    not item['name'].endswith("UNPROCESSED"):
                obj = swift_client.get_object("ironic-inspector", item['name'])
                ret.append((item['name'], obj))

        return ret
