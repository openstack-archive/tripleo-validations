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

from tripleo_validations import utils


DOCUMENTATION = """
    lookup: nova_hypervisor_statistics
    description: Retrieve hypervisor statistic information from Nova
    long_description:
      - Load hypervisor statistics using the Nova API.
    author: Brad P. Crochet <brad@redhat.com>
"""

EXAMPLES = """
    - name: Get all hypervisor statistics from nova
      debug:
        msg: |
             {{ lookup('nova_hypervisor_statistics') }}
"""

RETURN = """
_raw:
    description: A Python list with results from the API call.
"""


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns server information from nova."""
        nova = utils.get_nova_client(variables)
        statistics = nova.hypervisor_stats.statistics()
        return utils.filtered(statistics)
