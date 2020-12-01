#   Copyright 2015 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import os

DEFAULT_VALIDATIONS_BASEDIR = "/usr/share/ansible"
DEFAULT_VALIDATIONS_LEGACY_BASEDIR = "/usr/share/openstack-tripleo-validations"

VALIDATIONS_LOG_BASEDIR = '/var/log/validations'

ANSIBLE_VALIDATION_DIR = (
    os.path.join(DEFAULT_VALIDATIONS_LEGACY_BASEDIR, 'playbooks')
    if os.path.exists(os.path.join(DEFAULT_VALIDATIONS_LEGACY_BASEDIR,
                                   'playbooks'))
    else "/usr/share/ansible/validation-playbooks"
    )


VALIDATION_GROUPS_INFO = (
        '/usr/share/ansible/groups.yaml'
        if os.path.exists('/usr/share/ansible/groups.yaml')
        else os.path.join(DEFAULT_VALIDATIONS_LEGACY_BASEDIR, 'groups.yaml')
        )

# TRIPLEO_META_USAGE_KEY is inserted into metadata for containers created in
# Swift via SwiftPlanStorageBackend to identify them from other containers
TRIPLEO_META_USAGE_KEY = 'x-container-meta-usage-tripleo'
