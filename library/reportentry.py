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

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: reportentry
short_description: Print a custom report
description:
    - Print a custom report
options:
    report_status:
        required: true
        description:
          - The report status. Should be 'OK', 'ERROR' or 'SKIPPED'.
        choices:
          - 'OK'
          - 'ERROR'
          - 'SKIPPED'
        type: str
    report_reason:
        required: true
        description:
          - The reason of the report
        type: str
    report_recommendations:
        required: true
        description:
          - A list of recommendations to do.
        type: list
author: "Gael Chamoulaud"
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
  - name: Report DNS setup in undercloud.conf
    reportentry:
      report_status: "ERROR"
      report_reason: "DNS is not setup correctly in undercloud.conf"
      report_recommendations:
        - "Please set the 'undercloud_nameservers' param in undercloud.conf"
'''


def format_msg_report(status, reason, recommendations):
    msg = ("[{}] '{}'\n".format(status, reason))
    if recommendations:
        for rec in recommendations:
            msg += " - RECOMMENDATION: {}\n".format(rec)

    return msg


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    status = module.params.get('report_status')
    msg = format_msg_report(module.params.get('report_status'),
                            module.params.get('report_reason'),
                            module.params.get('report_recommendations'))

    if status == 'ERROR':
        module.fail_json(msg=msg)
    elif status == "SKIPPED":
        module.exit_json(changed=False,
                         warnings=msg)
    else:
        module.exit_json(changed=False,
                         msg=msg)


if __name__ == '__main__':
    main()
