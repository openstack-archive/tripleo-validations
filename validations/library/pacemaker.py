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

from xml.etree import ElementTree

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: pacemaker
short_description: Return status from a pacemaker status XML
description:
    - Return status from a pacemaker status XML
options:
    status:
        required: true
        description:
           - pacemaker status XML
        type: str
author: "Tomas Sedovic"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
  - name: Get pacemaker status
    become: true
    command: pcs status xml
    register: pcs_status
  - name: Check pacemaker status
    pacemaker: status="{{ pcs_status.stdout }}"
'''


def parse_pcs_status(pcs_status_xml):
    root = ElementTree.fromstring(pcs_status_xml)
    result = {
        'failures': root.findall('failures/failure'),
    }
    return result


def format_failure(failure):
    return ("Task {task} {op_key} failed on node {node}. Exit reason: "
            "'{exitreason}'. Exit status: '{exitstatus}'."
            .format(task=failure.get('task'),
                    op_key=failure.get('op_key'),
                    node=failure.get('node'),
                    exitreason=failure.get('exitreason'),
                    exitstatus=failure.get('exitstatus')))


def main():
    module = AnsibleModule(argument_spec=dict(
        status=dict(required=True, type='str'),
    ))

    pcs_status = parse_pcs_status(module.params.get('status'))
    failures = pcs_status['failures']
    failed = len(failures) > 0
    if failed:
        msg = "The pacemaker status contains some failed actions:\n" +\
              '\n'.join((format_failure(failure) for failure in failures))
    else:
        msg = "The pacemaker status reports no errors."
    module.exit_json(
        failed=failed,
        msg=msg,
    )


if __name__ == '__main__':
    main()
