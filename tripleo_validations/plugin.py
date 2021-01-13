#   Copyright 2013 Nebula Inc.
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
#

"""OpenStackClient Plugin interface"""

import logging

from osc_lib import utils


LOG = logging.getLogger(__name__)

DEFAULT_TRIPLEO_VALIDATION_API_VERSION = '2'

# Required by the OSC plugin interface
API_NAME = 'tripleo_validations'
API_VERSION_OPTION = 'os_tripleo_validations_api_version'
API_VERSIONS = {
    '2': 'tripleo_validations.plugin'
}


# Required by the OSC plugin interface
def build_option_parser(parser):
    """Hook to add global options

    Called from openstackclient.shell.OpenStackShell.__init__()
    after the builtin parser has been initialized.  This is
    where a plugin can add global options such as an API version setting.

    :param argparse.ArgumentParser parser: The parser object that has been
        initialized by OpenStackShell.
    """
    parser.add_argument(
        '--os-tripleo-validations-api-version',
        metavar='<tripleo-validations-api-version>',
        default=utils.env(
            'OS_TRIPLEO_VALIDATIONS_API_VERSION',
            default=DEFAULT_TRIPLEO_VALIDATION_API_VERSION),
        help=("TripleO Client API version, default={}"
              " (Env: DEFAULT_TRIPLEO_VALIDATION_API_VERSION)").format(
            DEFAULT_TRIPLEO_VALIDATION_API_VERSION))
    return parser
