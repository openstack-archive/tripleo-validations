#!/usr/bin/env python

# Copyright 2018 Red Hat, Inc.
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
from glanceclient import client as glance_client
from glanceclient.exc import HTTPNotFound

from tripleo_validations.utils import get_auth_session


DOCUMENTATION = """
    lookup: glance_images
    description: Retrieve image information from Glance
    long_description:
      - Load image information using the Glance API and search by attribute.
    options:
      _terms:
        description: Optional filter attribute and filter value
    author: Brad P. Crochet <brad@redhat.com>
"""

EXAMPLES = """
    - name: Get all image ids from glance
      debug:
        msg: |
             {{ lookup('glance_images', wantlist=True) |
             map(attribute='id') | join(', ') }}

    - name: Get image with name 'overcloud-full'
      debug:
        msg: |
             {{ lookup('glance_images', 'name', ['overcloud-full'],
             wantlist=True) | map(attribute='name') }}"
"""

RETURN = """
_raw:
    description: A Python list with results from the API call.
"""


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns server information from nova."""
        auth_url = variables.get('auth_url')
        username = variables.get('username')
        project_name = variables.get('project_name')
        token = variables.get('os_auth_token')
        session = get_auth_session(auth_url, username, project_name,
                                   auth_token=token)
        glance = glance_client.Client(2, session=session)

        images = []
        if len(terms) > 0:
            # Look up images by name
            if terms[0] == 'name':
                for value in terms[1]:
                    try:
                        search_data = {terms[0]: value}
                        images.extend(
                            [image for image in
                             glance.images.list(filters=search_data)]
                        )
                    except HTTPNotFound:
                        pass
        else:
            images = [image for image in glance.images.list()]

        return images
