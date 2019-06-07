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

import os

from ansible.plugins.lookup import LookupBase

from tripleo_validations import utils


EXCLUDED_EXT = (
    '.pyc',
    '.pyo',
)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        """Returns the current plan files.

        Returns a list of tuples, one for each plan file,
        containing the template path and the template content.
        """
        ret = []
        swift = utils.get_swift_client(variables)
        container = swift.get_container(variables['plan'])
        for item in container[1]:
            obj = swift.get_object(variables['plan'], item['name'])
            try:
                obj = (obj[0], obj[1].decode('utf-8'))
            except AttributeError:
                pass

            if os.path.splitext(item['name'])[-1] not in EXCLUDED_EXT:
                ret.append((item['name'], obj))

        return ret
