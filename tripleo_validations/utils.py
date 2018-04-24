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

from __future__ import print_function

import collections

from keystoneauth1.identity import generic as ks_id
from keystoneauth1 import session
from swiftclient.client import Connection


def get_auth_session(auth_url, username, project_name, password=None,
                     auth_token=None, cacert=None):
    if auth_token:
        auth = ks_id.Token(auth_url=auth_url,
                           token=auth_token,
                           project_name=project_name,
                           project_domain_id='default')
    else:
        auth = ks_id.Password(auth_url=auth_url,
                              username=username,
                              password=password,
                              project_name=project_name,
                              user_domain_id='default',
                              project_domain_id='default')
    return session.Session(auth=auth, verify=cacert)


def get_swift_client(preauthurl, preauthtoken):
    return Connection(preauthurl=preauthurl,
                      preauthtoken=preauthtoken,
                      retries=10,
                      starting_backoff=3,
                      max_backoff=120)


def get_nested(data, name, path):
    # Finds and returns a property from a nested dictionary by
    # following a path of a defined set of property names and types.

    def deep_find_key(key_data, data, name):
        key, instance_type, instance_name = key_data
        if key in data.keys():
            if not isinstance(data[key], instance_type):
                raise ValueError("The '{}' property of '{}' must be a {}."
                                 "".format(key, name, instance_name))
            return data[key]
        for item in data.values():
            if isinstance(item, collections.Mapping):
                return deep_find_key(key_data, item, name)
        return None

    if not isinstance(data, collections.Mapping):
        raise ValueError(
            "'{}' is not a valid resource.".format(name))

    current_value = data
    while len(path) > 0:
        key_data = path.pop(0)
        current_value = deep_find_key(key_data, current_value, name)
        if current_value is None:
            break

    return current_value
