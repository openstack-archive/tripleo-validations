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
import six
import yaml

DEFAULT_METADATA = {
    'name': 'Unnamed',
    'description': 'No description',
    'groups': [],
}


def get_validation_metadata(validation, key):
    """Returns metadata dictionary"""
    try:
        return validation['vars']['metadata'][key]
    except KeyError:
        return DEFAULT_METADATA.get(key)


def get_include_role(validation):
    """Returns Included Role"""
    try:
        if 'tasks' in validation:
            return validation['tasks'][0]['include_role']['name']
        return validation['roles'][0]
    except KeyError:
        return list()


def get_remaining_metadata(validation):
    try:
        return {k: v for k, v in validation['vars']['metadata'].items()
                if k not in ['name', 'description', 'groups']}
    except KeyError:
        return dict()


def get_validation_parameters(validation):
    """Returns parameters"""
    try:
        return {k: v for k, v in validation['vars'].items()
                if k != 'metadata'}
    except KeyError:
        return dict()


def build_summary(group, validations):
    """Creates validations documentation contents by group"""
    entries = [
        "* :ref:`{}`: {}".format(group + '_' + validation['id'],
                                 validation['name'])
        for validation in validations
    ]
    with open('doc/source/validations-{}.rst'.format(group), 'w') as f:
        f.write("\n".join(entries))
        f.write("\n")


def format_dict(my_dict):
    return ''.join(['\n\n  - **{}**: {}'.format(key, value)
                    for key, value in my_dict.items()])


def role_doc_entry(role_name, local_roles):
    """Generates Documentation entry

    If the included role isn't hosted on tripleo-validations, we point to the
    validations-common role documentation. Otherwise, it generates a classical
    local toctree.
    """
    local_role_doc = (".. toctree::\n\n"
                      "   roles/role-{}".format(role_name))
    doc_base_url = "https://docs.openstack.org/validations-common/latest/roles"
    external_role = \
        ("- `{role} <{baseurl}/role-{role}.html>`_ "
         "from `openstack/validations-common "
         "<https://opendev.org/openstack/validations-common>`_"
         "".format(role=role_name,
                   baseurl=doc_base_url))

    if role_name not in local_roles:
        return external_role
    return local_role_doc


def build_detail(group, validations, local_roles):
    entries = ['{}\n{}\n'.format(group, len(group) * '=')]
    entries = entries + [
        """.. _{label}:

{title}
{adornment}

{name}.

{desc}

- **hosts**: {hosts}
- **groups**: {groups}
- **parameters**:{parameters}
- **roles**: {roles}

Role documentation

{roledoc}
"""
        .format(label=(group + '_' + validation['id']),
                title=validation['id'],
                adornment=(len(validation['id']) * '-'),
                name=validation['name'],
                desc=validation['description'],
                groups=', '.join(validation['groups']),
                hosts=validation['hosts'],
                parameters=format_dict(validation['parameters']),
                roles=validation['roles'],
                roledoc=role_doc_entry(validation['roles'], local_roles)
                )
        for validation in validations]
    with open('doc/source/validations-{}-details.rst'.format(group), 'w') as f:
        f.write("\n".join(entries))


def build_groups_detail(groups):
    entries = [
        """
{group}
{adornment}

{desc}

.. include:: {link}

"""
        .format(group=grp.capitalize(),
                adornment=(len(grp) * '~'),
                link="validations-{}.rst".format(grp),
                desc=desc[0].get('description', None),
                )
        for grp, desc in sorted(groups.items())]
    with open('doc/source/validations-groups.rst', 'w') as f:
        f.write("\n".join(entries))


def parse_groups_file():
    contents = {}
    groups_file_path = os.path.abspath('groups.yaml')

    if os.path.exists(groups_file_path):
        with open(groups_file_path, "r") as grps:
            contents = yaml.safe_load(grps)

    return contents


def get_groups():
    # Seed it with the known groups from groups.yaml file.
    groups = set()
    contents = parse_groups_file()

    for group_name in six.iterkeys(contents):
        groups.add(group_name)

    return groups, contents


def get_local_roles(path):
    """Returns a list of local Ansible Roles"""
    return next(os.walk(path))[1]


def setup(app):
    group_name, group_info = get_groups()
    build_groups_detail(group_info)

    local_roles = get_local_roles(os.path.abspath('roles'))

    validations = []
    for validation_path in sorted(glob('playbooks/*.yaml')):
        with open(validation_path) as f:
            loaded_validation = yaml.safe_load(f.read())[0]
            for group in get_validation_metadata(loaded_validation, 'groups'):
                group_name.add(group)
            validations.append({
                'hosts': loaded_validation['hosts'],
                'parameters': get_validation_parameters(loaded_validation),
                'id': os.path.splitext(
                    os.path.basename(validation_path))[0],
                'name': get_validation_metadata(loaded_validation, 'name'),
                'groups': get_validation_metadata(loaded_validation, 'groups'),
                'description': get_validation_metadata(loaded_validation,
                                                       'description'),
                'metadata': get_remaining_metadata(loaded_validation),
                'roles': get_include_role(loaded_validation)
            })

    for group in group_name:
        validations_in_group = [validation for validation
                                in validations
                                if group in validation['groups']]
        build_detail(group, validations_in_group, local_roles)
        build_summary(group, validations_in_group)
