#!/usr/bin/env python

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

import netaddr

from ansible.module_utils.basic import *  # NOQA


def main():
    module = AnsibleModule(argument_spec=dict(
        start=dict(required=True, type='str'),
        end=dict(required=True, type='str'),
        min_size=dict(required=True, type='int'),
    ))

    start = module.params.get('start')
    end = module.params.get('end')

    iprange = netaddr.IPRange(start, end)

    if len(iprange) < module.params.get('min_size'):
        module.exit_json(
            changed=True,
            warnings=[
                'The IP range {} - {} contains {} addresses.'.format(
                    start, end, len(iprange)),
                'This might not be enough for the deployment or later scaling.'
            ])
    else:
        module.exit_json(msg='success')


if __name__ == '__main__':
    main()
