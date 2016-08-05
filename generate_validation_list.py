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
from os import path

import six
import yaml


def metadata(validation, metadata_name):
    return validation['vars']['metadata'][metadata_name]


def setup(app):
    # Seed it with the known groups:
    groups = set(('prep', 'pre-introspection',
                  'pre-deployment', 'post-deployment'))
    validations = {}
    for validation_path in glob('validations/*.yaml'):
        with open(validation_path) as f:
            loaded_validation = yaml.safe_load(f.read())[0]
            for group in metadata(loaded_validation, 'groups'):
                groups.add(group)
                validations[path.basename(validation_path)] = loaded_validation

    for group in groups:
        validations_in_group = [(filename, validation) for filename, validation
                                in six.iteritems(validations)
                                if group in metadata(validation, 'groups')]
        entries = ["* ``{}``: {}".format(name, metadata(validation, 'name'))
                   for name, validation in sorted(validations_in_group)]
        with open('doc/source/validations-{}.rst'.format(group), 'w') as f:
            f.write("\n".join(entries))
