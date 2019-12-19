import os
import six
import yaml

from ansiblelint import AnsibleLintRule


class ValidationHasMetadataRule(AnsibleLintRule):
    id = '750'
    shortdesc = 'Validation playbook must have mandatory metadata'

    info = """
---
- hosts: localhost
  vars:
    metadata:
      name: Validation Name
      description: >
        A full description of the validation.
      groups:
        - group1
        - group2
        - group3
"""

    description = (
        "The Validation playbook must have mandatory metadata:\n"
        "```{}```".format(info)
    )

    severity = 'HIGH'
    tags = ['metadata']

    no_vars_found = "The validation playbook must contain a 'vars' dictionary"
    no_meta_found = (
        "The validation playbook must contain "
        "a 'metadata' dictionary under vars"
    )
    no_groups_found = \
        "*metadata* should contain a list of group (groups)"

    unknown_groups_found = (
        "Unkown group(s) '{}' found! "
        "The official list of groups are '{}'. "
        "To add a new validation group, please add it in the groups.yaml "
        "file at the root of the tripleo-validations project."
    )

    def get_groups(self):
        """Returns a list of group names supported by
        tripleo-validations by reading 'groups.yaml'
        file located in the base direcotry.
        """
        results = []

        grp_file_path = os.path.abspath('groups.yaml')

        with open(grp_file_path, "r") as grps:
            contents = yaml.safe_load(grps)

        for grp_name, grp_desc in sorted(contents.items()):
            results.append(grp_name)

        return results

    def matchplay(self, file, data):
        results = []
        path = file['path']

        if file['type'] == 'playbook':
            if path.startswith("playbooks/") or \
               path.find("tripleo-validations/playbooks/") > 0:

                # *hosts* line check
                hosts = data.get('hosts', None)
                if not hosts:
                    return [({
                        path: data
                    }, "No *hosts* key found in the playbook")]

                # *vars* lines check
                vars = data.get('vars', None)
                if not vars:
                    return [({
                        path: data
                    }, self.no_vars_found)]
                else:
                    if not isinstance(vars, dict):
                        return [({path: data}, '*vars* should be a dictionary')]

                    # *metadata* lines check
                    metadata = data['vars'].get('metadata', None)
                    if metadata:
                        if not isinstance(metadata, dict):
                            return [(
                                {path: data},
                                '*metadata* should be a dictionary')]
                    else:
                        return [({path: data}, self.no_meta_found)]

                    # *metadata>[name|description] lines check
                    for info in ['name', 'description']:
                        if not metadata.get(info, None):
                            results.append((
                                {path: data},
                                '*metadata* should contain a %s key' % info))
                            continue
                        if not isinstance(metadata.get(info),
                                          six.string_types):
                            results.append((
                                {path: data},
                                '*%s* should be a string' % info))

                    # *metadata>groups* lines check
                    if not metadata.get('groups', None):
                        results.append((
                            {path: data},
                            self.no_groups_found))
                    else:
                        if not isinstance(metadata.get('groups'), list):
                            results.append((
                                {path: data},
                                '*groups* should be a list'))
                        else:
                            groups = metadata.get('groups')
                            group_list = self.get_groups()
                            unknown_groups_list = list(
                                set(groups) - set(group_list))
                            if unknown_groups_list:
                                results.append((
                                    {path: data},
                                    self.unknown_groups_found.format(
                                        unknown_groups_list,
                                        group_list)
                                ))
            return results

        return results
