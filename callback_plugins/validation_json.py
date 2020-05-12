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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import datetime
import json
import time
import os

from functools import partial

from ansible.module_utils.six.moves import reduce
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase

DOCUMENTATION = '''
    callback: json
    short_description: Ansible screen output as JSON file
    version_added: "1.0"
    description:
        - This callback converts all events into a JSON file
          stored in /var/log/validations
    type: stdout
    requirements: None
'''

VALIDATIONS_LOG_DIR = "/var/log/validations"


def current_time():
    return '%sZ' % datetime.datetime.utcnow().isoformat()


def secondsToStr(t):
    def rediv(ll, b):
        return list(divmod(ll[0], b)) + ll[1:]

    return "%d:%02d:%02d.%03d" % tuple(
        reduce(rediv, [[
            t * 1000,
        ], 1000, 60, 60]))


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'validation_json'

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)
        self.results = []
        self.simple_results = []
        self.env = {}
        self.t0 = None
        self.current_time = current_time()

    def _new_play(self, play):
        return {
            'play': {
                'host': play.get_name(),
                'validation_id': self.env['playbook_name'],
                'validation_path': self.env['playbook_path'],
                'id': (os.getenv('ANSIBLE_UUID') if os.getenv('ANSIBLE_UUID')
                       else str(play._uuid)),
                'duration': {
                    'start': current_time()
                }
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.get_name(),
                'id': str(task._uuid),
                'duration': {
                    'start': current_time()
                }
            },
            'hosts': {}
        }

    def _val_task(self, task_name):
        return {
            'task': {
                'name': task_name,
                'hosts': {}
            }
        }

    def _val_task_host(self, task_name):
        return {
            'task': {
                'name': task_name,
                'hosts': {}
            }
        }

    def v2_playbook_on_start(self, playbook):
        self.t0 = time.time()
        pl = playbook._file_name
        validation_id = os.path.splitext(os.path.basename(pl))[0]
        self.env = {
            "playbook_name": validation_id,
            "playbook_path": playbook._basedir
        }

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

    def v2_playbook_on_handler_task_start(self, task):
        self.results[-1]['tasks'].append(self._new_task(task))

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())

        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s

        output = {
            'plays': self.results,
            'stats': summary,
            'validation_output': self.simple_results
        }

        log_file = "{}/{}_{}_{}.json".format(
            VALIDATIONS_LOG_DIR,
            (os.getenv('ANSIBLE_UUID') if os.getenv('ANSIBLE_UUID') else
             self.results[0].get('play').get('id')),
            self.env['playbook_name'],
            self.current_time)

        with open(log_file, 'w') as js:
            js.write(json.dumps(output,
                                cls=AnsibleJSONEncoder,
                                indent=4,
                                sort_keys=True))

    def _record_task_result(self, on_info, result, **kwargs):
        """This function is used as a partial to add
           failed/skipped info in a single method
        """
        host = result._host
        task = result._task
        task_result = result._result.copy()
        task_result.update(on_info)
        task_result['action'] = task.action
        self.results[-1]['tasks'][-1]['hosts'][host.name] = task_result

        if 'failed' in task_result.keys():
            self.simple_results.append(self._val_task(task.name))
            self.simple_results[-1]['task']['status'] = "FAILED"
            self.simple_results[-1]['task']['hosts'][host.name] = task_result
        if 'warnings' in task_result.keys():
            self.simple_results.append(self._val_task(task.name))
            self.simple_results[-1]['task']['status'] = "WARNING"
            self.simple_results[-1]['task']['hosts'][host.name] = task_result

        end_time = current_time()
        time_elapsed = secondsToStr(time.time() - self.t0)
        self.results[-1]['tasks'][-1]['task']['duration']['end'] = end_time
        self.results[-1]['play']['duration']['end'] = end_time
        self.results[-1]['play']['duration']['time_elapsed'] = time_elapsed

    def __getattribute__(self, name):
        """Return ``_record_task_result`` partial with a dict
           containing skipped/failed if necessary
        """
        if name not in ('v2_runner_on_ok', 'v2_runner_on_failed',
                        'v2_runner_on_unreachable', 'v2_runner_on_skipped'):
            return object.__getattribute__(self, name)

        on = name.rsplit('_', 1)[1]

        on_info = {}
        if on in ('failed', 'skipped'):
            on_info[on] = True

        return partial(self._record_task_result, on_info)
