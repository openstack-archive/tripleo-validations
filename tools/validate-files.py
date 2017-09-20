#!/usr/bin/env python
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import os
import sys


def exit_usage():
    print('Usage %s <directory>' % sys.argv[0])
    sys.exit(1)


def validate_library_file(file_path):
    with open(file_path) as f:
        file_content = f.read()
        if 'DOCUMENTATION = ' not in file_content \
                or 'EXAMPLES = ' not in file_content:
            if quiet < 1:
                print('Missing ansible documentation in %s' % file_path)
            return 1
    return 0


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--quiet', '-q',
                   action='count',
                   help='output warnings and errors (-q) or only errors (-qq)')

    p.add_argument('path_args',
                   nargs='*',
                   default=['.'])

    return p.parse_args()

args = parse_args()
path_args = args.path_args
quiet = args.quiet
exit_val = 0
failed_files = []

for base_path in path_args:
    if os.path.isdir(base_path):
        for subdir, dirs, files in os.walk(base_path):
            if '.tox' in dirs:
                dirs.remove('.tox')
            if '.git' in dirs:
                dirs.remove('.git')
            for f in files:
                if f.endswith('.py') \
                        and not f == '__init__.py' \
                        and os.path.join('validations', 'library') in subdir:
                    file_path = os.path.join(subdir, f)
                    if quiet < 1:
                        print('Validating %s' % file_path)
                    failed = validate_library_file(file_path)
                    if failed:
                        failed_files.append(file_path)
                    exit_val |= failed
    else:
        print('Unexpected argument %s' % base_path)
        exit_usage()

if failed_files:
    print('Validation failed on:')
    for f in failed_files:
        print(f)
else:
    print('Validation successful!')
sys.exit(exit_val)
