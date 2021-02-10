# Copyright 2016 Red Hat, Inc.
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

from unittest.mock import MagicMock
from unittest.mock import patch

import library.check_other_processes_pmd_usage as validation
from tripleo_validations.tests import base


class TestOtherProcessesPmdusageCheck(base.TestCase):

    def setUp(self):
        super(TestOtherProcessesPmdusageCheck, self).setUp()
        self.module = MagicMock()

    @patch('library.check_other_processes_pmd_usage.'
           'check_current_process_pmd_usage')
    def test_validate_no_other_processes_pmd_usage(self, mock_number_list):
        mock_number_list.side_effect = [[], []]
        pmd_cpus = ["2", "3"]
        current_processes = "21's 4-7\n22's 4-9\n24's 4-5"
        pmd_processes = "22's 4-9"
        self.module.run_command.side_effect = [[0, current_processes, ""],
                                               [0, pmd_processes, ""]]
        exclude_processes_pid = ["24"]
        validation.check_other_processes_pmd_usage(self.module, pmd_cpus,
                                                   exclude_processes_pid)
        self.module.exit_json.assert_called_with(
            messages=[],
            pmd_interrupts=False)

    @patch('library.check_other_processes_pmd_usage.'
           'check_current_process_pmd_usage')
    def test_validate_with_no_current_processes(self, mock_number_list):
        mock_number_list.side_effect = [[], []]
        pmd_cpus = ["2", "3"]
        current_processes = ""
        pmd_processes = "22's 4-9"
        self.module.run_command.side_effect = [None,
                                               [0, pmd_processes, ""]]
        exclude_processes_pid = ["24"]
        validation.check_other_processes_pmd_usage(self.module, pmd_cpus,
                                                   exclude_processes_pid)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine current processes")

    @patch('library.check_other_processes_pmd_usage.'
           'check_current_process_pmd_usage')
    def test_validate_with_no_pmd_processes(self, mock_number_list):
        mock_number_list.return_value = []
        pmd_cpus = ["2", "3"]
        current_processes = "21's 2-5\n22's 4-9\n24's 4-5"
        pmd_processes = ""
        self.module.run_command.side_effect = [[0, current_processes, ""],
                                               None]
        exclude_processes_pid = ["24"]
        validation.check_other_processes_pmd_usage(self.module, pmd_cpus,
                                                   exclude_processes_pid)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine PMD threads processes")

    @patch('library.check_other_processes_pmd_usage.'
           'check_current_process_pmd_usage')
    def test_validate_other_processes_pmd_usage(self, mock_number_list):
        mock_number_list.side_effect = [["pmd threads: 2,3 used in process: 21"], []]
        pmd_cpus = ["2", "3"]
        current_processes = "21's 2-5\n22's 4-9\n24's 4-5"
        pmd_processes = "22's 4-9"
        self.module.run_command.side_effect = [[0, current_processes, ""],
                                               [0, pmd_processes, ""]]
        exclude_processes_pid = ["24"]
        validation.check_other_processes_pmd_usage(self.module, pmd_cpus,
                                                   exclude_processes_pid)
        self.module.exit_json.assert_called_with(
            messages=["pmd threads: 2,3 used in process: 21"],
            pmd_interrupts=True)

    def test_check_current_process_pmd_usage(self):
        pmd_cpus = ["2", "3"]
        process_id = "21"
        range_list = "2-5,8-11"
        expected_value = ["pmd threads: 2,3 used in process: 21"]
        result = validation.check_current_process_pmd_usage(self.module, pmd_cpus,
                                                            process_id, range_list)
        self.assertEqual(result, expected_value)

    def test_check_current_process_pmd_usage_with_exclude_value(self):
        pmd_cpus = ["2", "3"]
        process_id = "21"
        range_list = "2-5,8-11,^8"
        expected_value = ["pmd threads: 2,3 used in process: 21"]
        result = validation.check_current_process_pmd_usage(self.module, pmd_cpus,
                                                            process_id, range_list)
        self.assertEqual(result, expected_value)

    def test_check_current_process_pmd_usage_with_invalid_range(self):
        pmd_cpus = ["2", "3"]
        process_id = "21"
        range_list = "2-5,-"
        result = validation.check_current_process_pmd_usage(self.module, pmd_cpus,
                                                            process_id, range_list)
        self.module.fail_json.assert_called_with(
            msg="Invalid number in input param 'range_list': invalid literal for int() with base 10: ''")
