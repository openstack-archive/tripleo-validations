import os
import yaml
from ansiblelint.errors import MatchError
from ansiblelint.rules import AnsibleLintRule


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
      categories:
        - category1
        - category2
        - category3
      products:
        - product1
        - product2
        - product3
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
    no_classification_found = \
        "*metadata* should contain a list of {classification}"

    unknown_classifications_found = (
        "Unkown {classification_key}(s) '{unknown_classification}' found! "
        "The official list of {classification_key} are '{known_classification}'. "
    )

    how_to_add_classification = {
        'groups': (
            "To add a new validation group, please add it in the groups.yaml "
            "file at the root of the tripleo-validations project."
        )
    }

    def get_classifications(self, classification='groups'):
        """Returns a list classification names
        defined for tripleo-validations in the '{classification}.yaml' file
        located in the base repo directory.
        """
        file_path = os.path.abspath(classification + '.yaml')

        try:
            with open(file_path, "r") as definitions:
                contents = yaml.safe_load(definitions)
        except (PermissionError, OSError):
            raise RuntimeError(
                "{}.yaml file at '{}' inacessible.".format(
                    classification,
                    file_path))

        results = [name for name, _ in contents.items()]

        return results

    def check_classification(self, metadata, path,
                             classification_key, strict=False):
        """Check validatity of validation classifications,
        such as groups, categories and products.
        This one is tricky.
        Empty lists in python evaluate as false
        So we can't just check for truth value of returned list.
        Instead we have to compare the returned value with `None`.
        """
        classification = metadata.get(classification_key, None)

        if classification is None:
            return MatchError(
                message=self.no_classification_found.format(
                    classification=classification_key
                ),
                filename=path,
                details=str(metadata))
        else:
            if not isinstance(classification, list):
                return MatchError(
                    message="*{}* must be a list".format(classification_key),
                    filename=path,
                    details=str(metadata))
            elif strict:
                classifications = self.get_classifications(classification_key)
                unknown_classifications = list(
                    set(classification) - set(classifications))
                if unknown_classifications:
                    message = self.unknown_classifications_found.format(
                        unknown_classification=unknown_classifications,
                        known_classification=classifications,
                        classification_key=classification_key)
                    message += self.how_to_add_classification.get(classification_key, "")
                    return MatchError(
                        message=message,
                        filename=path,
                        details=str(metadata))

    def matchplay(self, file, data):
        results = []
        path = file['path']

        if file['type'] == 'playbook':
            if path.startswith("playbooks/") \
               or "tripleo-validations/playbooks/" in path:

                # *hosts* line check
                hosts = data.get('hosts', None)
                if not hosts:
                    results.append(
                        MatchError(
                            message="No *hosts* key found in the playbook",
                            filename=path,
                            details=str(data)))

                # *vars* lines check
                vars = data.get('vars', None)
                if not vars:
                    results.append(
                        MatchError(
                            message=self.no_vars_found,
                            filename=path,
                            details=str(data)))
                else:
                    if not isinstance(vars, dict):
                        results.append(
                            MatchError(
                                message='*vars* must be a dictionary',
                                filename=path,
                                details=str(data)))

                    # *metadata* lines check
                    metadata = data['vars'].get('metadata', None)
                    if metadata:
                        if not isinstance(metadata, dict):
                            results.append(
                                MatchError(
                                    message='*metadata* must be a dictionary',
                                    filename=path,
                                    details=str(data)))
                    else:
                        results.append(
                            MatchError(
                                message=self.no_meta_found,
                                filename=path,
                                details=str(data)))

                    # *metadata>[name|description] lines check
                    for info in ['name', 'description']:
                        if not metadata.get(info, None):
                            results.append(
                                MatchError(
                                    message='*metadata* must contain a %s key' % info,
                                    filename=path,
                                    details=str(data)))
                            continue
                        if not isinstance(metadata.get(info), str):
                            results.append(
                                MatchError(
                                    message='*%s* should be a string' % info,
                                    filename=path,
                                    details=str(data)))

                    #Checks for metadata we use to classify validations.
                    #Groups, categories and products
                    for classification in ['categories', 'products', 'groups']:
                        classification_error = self.check_classification(
                            metadata,
                            path,
                            classification,
                            strict=(classification == 'groups'))

                        if classification_error:
                            results.append(classification_error)

        return results
