# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from glob import glob
import os

import yaml

DEFAULT_METADATA = {
    'name': 'Unnamed',
    'description': 'No description',
    'groups': [],
}


def get_validation_metadata(validation, key):
    try:
        return validation['vars']['metadata'][key]
    except KeyError:
        return DEFAULT_METADATA.get(key)


def get_remaining_metadata(validation):
    try:
        return {k: v for k, v in validation['vars']['metadata'].items()
                if k not in ['name', 'description', 'groups']}
    except KeyError:
        return dict()


def get_validation_parameters(validation):
    try:
        return {k: v for k, v in validation['vars'].items()
                if k != 'metadata'}
    except KeyError:
        return dict()


def build_summary(group, validations):
    entries = ["* :ref:`{}`: {}".format(group + '_' + validation['id'], validation['name'])
               for validation in validations]
    with open('doc/source/validations-{}.rst'.format(group), 'w') as f:
        f.write("\n".join(entries))


def format_dict(my_dict):
    return ''.join(['\n\n  - **{}**: {}'.format(key, value)
                    for key, value in my_dict.items()])


def build_detail(group, validations):
    entries = ['{}\n{}\n'.format(group, len(group) * '=')]
    entries = entries + [
        """.. _{label}:

{title}
{adornment}

{name}.

{desc}

- **hosts**: {hosts}
- **groups**: {groups}
- **metadata**: {metadata}
- **parameters**: {parameters}

`View validation source code <http://git.openstack.org/cgit/openstack/tripleo-validations/plain/validations/{title}.yaml>`__.

"""
        .format(label=(group + '_' + validation['id']),
                title=validation['id'],
                adornment=(len(validation['id']) * '-'),
                name=validation['name'],
                desc=validation['description'],
                groups=', '.join(validation['groups']),
                metadata=format_dict(validation['metadata']),
                hosts=validation['hosts'],
                parameters=format_dict(validation['parameters']),
                )
        for validation in validations]
    with open('doc/source/validations-{}-details.rst'.format(group), 'w') as f:
        f.write("\n".join(entries))


def setup(app):
    # Seed it with the known groups:
    groups = set(('prep', 'pre-introspection',
                  'pre-deployment', 'post-deployment',
                  'pre-update', 'pre-upgrade'))
    validations = []
    for validation_path in sorted(glob('validations/*.yaml')):
        with open(validation_path) as f:
            loaded_validation = yaml.safe_load(f.read())[0]
            for group in get_validation_metadata(loaded_validation, 'groups'):
                groups.add(group)
            validations.append({
                'hosts': loaded_validation['hosts'],
                'parameters': get_validation_parameters(loaded_validation),
                'id': os.path.splitext(
                    os.path.basename(validation_path))[0],
                'name': get_validation_metadata(loaded_validation, 'name'),
                'groups': get_validation_metadata(loaded_validation, 'groups'),
                'description': get_validation_metadata(loaded_validation,
                                                       'description'),
                'metadata': get_remaining_metadata(loaded_validation)
            })

    for group in groups:
        validations_in_group = [validation for validation
                                in validations
                                if group in validation['groups']]
        build_detail(group, validations_in_group)
        build_summary(group, validations_in_group)
