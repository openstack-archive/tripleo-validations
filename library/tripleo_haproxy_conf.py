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

import re

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: tripleo_haproxy_conf
short_description: Gather the HAProxy config
description:
    - Gather the HAProxy config
    - Owned by DFG:PIDONE
options:
    path:
        required: true
        description:
            - file path to the config file
        type: str
author: "Tomas Sedovic"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
    - name: Gather the HAProxy config
      tripleo_haproxy_conf: path=/etc/haproxy/haproxy.cfg
'''


def generic_ini_style_conf_parser(file_path, section_regex, option_regex):
    """
    ConfigParser chokes on both mariadb and haproxy files. Luckily, they have
    a syntax approaching ini config file so they are relatively easy to parse.
    This generic ini style config parser is not perfect, as it can ignore some
    valid options, but it is good enough for our use case.

    :return: parsed haproxy configuration
    :rtype: dict
    """
    config = {}
    current_section = None
    with open(file_path) as config_file:
        for line in config_file:
            match_section = re.match(section_regex, line)
            if match_section:
                current_section = match_section.group(1)
                config[current_section] = {}
            match_option = re.match(option_regex, line)
            if match_option and current_section:
                option = re.sub(r'\s+', ' ', match_option.group(1))
                config[current_section][option] = match_option.group(2)
    return config


def parse_haproxy_conf(file_path):
    """
    Provides section and option regex to the parser.
    Essentially a wrapper for generic_ini_style_conf_parser.
    Provides no extra functionality but simplifies the call, somewhat.

    :return: parsed haproxy configuration
    :rtype: dict

    ..note::

        Both regular expressions bellow are used for parsing haproxy.cfg,
        which has a rather vague syntax. The regexes are supposed to match all
        possibilities described here, and some more:
        https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/load_balancer_administration/ch-haproxy-setup-vsa
    """
    section_regex = r'^(\w+)'
    option_regex = r'^(?:\s+)(\w+(?:\s+\w+)*?)\s+([\w/]*)$'
    return generic_ini_style_conf_parser(file_path, section_regex,
                                         option_regex)


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    haproxy_conf_path = module.params.get('path')

    try:
        config = parse_haproxy_conf(haproxy_conf_path)
    except IOError:
        module.fail_json(msg="Could not open the haproxy conf file at: '%s'" %
                         haproxy_conf_path)

    module.exit_json(changed=False, ansible_facts={u'haproxy_conf': config})


if __name__ == '__main__':
    main()
