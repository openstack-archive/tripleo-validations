#!/usr/bin/env python
# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

""" Check for available updates for a given package."""

import collections
import subprocess

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: check_package_update
short_description: Check for available updates for a given package
options:
    package:
        required: true
        description:
            - The name of the package you want to check
        type: str
    pkg_mgr:
        required: true
        description:
            - Supported Package Manager, DNF or YUM
        type: str
author: "Florian Fuchs"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
    - name: Get available updates for packages
      check_package_update:
        package: python-tripleoclient
        pkg_mgr: {{ ansible_pkg_mgr}}
'''

SUPPORTED_PKG_MGRS = (
    'yum',
    'dnf',
)


PackageDetails = collections.namedtuple('PackageDetails',
                                        ['name', 'arch', 'version'])


def get_package_details(line):
    # Parses an output line from a package manager's
    # `list (available|installed)` command and returns
    # a named tuple
    parts = line.rstrip().split()
    name, arch = parts[0].split('.')
    # Version string, excluding release string and epoch
    version = parts[1].split('-')[0].split(':')[-1]
    return PackageDetails(name, arch, version)


def _command(command):
    # Return the result of a subprocess call
    # as [stdout, stderr]
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    return process.communicate()


def _get_installed_version_from_output(output, package):
    for line in output.split('\n'):
        if package in line:
            return get_package_details(line)


def _get_latest_available_versions(output, installed):
    # Returns the latest available minor and major versions,
    # one for each.
    latest_minor = None
    latest_major = None
    # Get all packages with the same architecture
    packages = list([get_package_details(line) for line in output.split('\n')
                     if '{i.name}.{i.arch}'.format(i=installed) in line])
    # Get all packages with the *same* major version
    minor = sorted((p for p in packages
                    if p.version[0] == installed.version[0]))
    if len(minor) > 0:
        latest_minor = minor[-1].version
    # Get all packages with a *higher* available major version
    major = sorted((p for p in packages
                    if p.version[0] > installed.version[0]))
    if len(major) > 0:
        latest_major = major[-1].version
    # If the output doesn't contain packages with the same major version
    # let's assume the currently installed version as latest minor one.
    if latest_minor is None:
        latest_minor = installed.version
    return latest_minor, latest_major


def check_update(module, package, pkg_mgr):
    if pkg_mgr not in SUPPORTED_PKG_MGRS:
        module.fail_json(
            msg='Package manager "{}" is not supported.'.format(pkg_mgr))
        return

    installed_stdout, installed_stderr = _command(
        [pkg_mgr, 'list', 'installed', package])
    # Fail the module if for some reason we can't lookup the current package.
    if installed_stderr != '':
        module.fail_json(msg=installed_stderr)
        return
    installed = _get_installed_version_from_output(installed_stdout, package)

    available_stdout, available_stderr = _command(
        [pkg_mgr, 'list', 'available', installed.name])
    latest_minor_version, latest_major_version = \
        _get_latest_available_versions(available_stdout, installed)

    module.exit_json(changed=False,
                     name=installed.name,
                     current_version=installed.version,
                     latest_minor_version=latest_minor_version,
                     latest_major_version=latest_major_version)


def main():
    module = AnsibleModule(argument_spec=dict(
        package=dict(required=True, type='str'),
        pkg_mgr=dict(required=True, type='str')
    ))

    check_update(module,
                 module.params.get('package'),
                 module.params.get('pkg_mgr'))


if __name__ == '__main__':
    main()
