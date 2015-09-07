# -*- coding: utf-8 -*-

import json
import sys

import py.path
import sarge

from .base import Capture


class PlaybookRunner(object):
    def __init__(self, playbook):
        self.playbook = playbook
        self.process = None
        self.skip_wait = False
        self.failures = []
        self.all_test_tasks_skipped = True

    def run_async(self):
        this_path = py.path.local(__file__)
        callback_plugin_path = this_path.dirpath('callback_plugin')

        env = self.playbook.env()
        additional_env = dict(
            PYTHONUNBUFFERED='1',
            ANSIBLE_CALLBACK_PLUGINS=str(callback_plugin_path),
            ANSIBLE_CALLBACK_WHITELIST='goodplay',
        )
        env.update(additional_env)

        cmd = sarge.shell_format(
            'ansible-playbook --verbose -i {0} {1}',
            self.playbook.inventory_path,
            self.playbook.playbook_path)

        self.process = sarge.run(cmd, env=env, stdout=Capture(), async=True)

        # wait for subprocess to be responsive
        self.process.wait_events()

    def wait(self):
        self.wait_for_event()

        for line in self.process.stdout:
            sys.stdout.write(line)

        self.process.wait()

        if self.all_test_tasks_skipped:
            self.failures.append('all test tasks have been skipped')

    def wait_for_event(self, event_name=None, **kwargs):
        for event in self.receive_events():
            if event['event_name'] == event_name:
                if all(item in event['data'].items()
                       for item in kwargs.items()):
                    return event
                else:  # pragma: no cover
                    message = 'found unexpected data in goodplay ' \
                        'event: {0!r}'.format(event)
                    raise Exception(message)
            elif event['event_name'] == 'error':
                error_message = event['data']['message']
                self.failures.append(error_message)
                self.skip_wait = True
                return
            else:  # pragma: no cover
                message = 'found unexpected goodplay event: {0!r}'.format(
                    event)
                raise Exception(message)

    def receive_events(self):
        event_line_prefix = 'GOODPLAY => '
        for line in self.process.stdout:
            sys.stdout.write(line)

            if line.startswith(event_line_prefix):
                event = json.loads(line[len(event_line_prefix):])
                yield event

    def wait_for_test_task(self, task):
        if self.skip_wait:
            return

        self.wait_for_event('test-task-start', name=task.name)

    def wait_for_test_task_outcome(self, task):
        if self.skip_wait:
            return

        event = self.wait_for_event('test-task-end', name=task.name)
        outcome = event['data']['outcome'] if event else 'skipped'

        if outcome != 'skipped':
            self.all_test_tasks_skipped = False

        return outcome
