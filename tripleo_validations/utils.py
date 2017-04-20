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
