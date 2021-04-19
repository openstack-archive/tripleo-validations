# Copyright 2021 Red Hat, Inc.
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

"""
test_glance_images
-----------------------------

Tests for `glance_images` module.
"""

try:
    from unittest import mock
except ImportError:
    import mock

from tripleo_validations.tests import fakes
from tripleo_validations.tests import base

import lookup_plugins.glance_images as plugin


class TestGlanceImages(base.TestCase):

    def setUp(self):
        super(TestGlanceImages, self).setUp()

    def test_module_init(self):
        """Verifying that the lookup plugin is instantiated properly.
        """

        lookup = plugin.LookupModule()

        module_attributes = dir(plugin)
        required_attributes = [
            'DOCUMENTATION',
            'EXAMPLES'
        ]

        self.assertTrue(set(required_attributes).issubset(module_attributes))

        self.assertIsInstance(plugin.DOCUMENTATION, str)
        self.assertIsInstance(plugin.EXAMPLES, str)

        self.assertIn('run', dir(lookup))
