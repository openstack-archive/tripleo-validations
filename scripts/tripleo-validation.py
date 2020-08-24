#!/usr/bin/env python

#   Copyright 2020 Red Hat, Inc.
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

import logging
from validations_common.validation import Validation

TRIPLEO_VALIDATION_DIR = "/usr/share/ansible/"


class TripleOValidation(Validation):
    """TripleO Validation client implementation class"""

    log = logging.getLogger(__name__ + ".TripleOValidation")

    def parser(self, tripleo_parser):
        """Argument parser for TripleO Validation"""
        parser = super(TripleOValidation, self).parser(tripleo_parser)
        # Check if user pass custom path for validation playbooks and
        # Ansible directory. If not, we override the value with the default
        # TripleO path.
        for action in tripleo_parser._actions:
            if action.dest == 'validation_dir':
                if action.default == parser.validation_dir:
                    parser.validation_dir = "{}/validation-playbooks".format(
                        TRIPLEO_VALIDATION_DIR)
                if action.dest == 'ansible_base_dir':
                    if action.default == parser.ansible_base_dir:
                        parser.ansible_base_dir = TRIPLEO_VALIDATION_DIR
        return parser


if __name__ == "__main__":
    validation = TripleOValidation()
    args = validation.parser(validation)
    validation.take_action(args)
