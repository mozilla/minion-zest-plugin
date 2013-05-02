# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import json
import os
import tempfile

from minion.plugin_api import ExternalProcessPlugin


class ZestPlugin(ExternalProcessPlugin):

    PLUGIN_NAME = "Zest"
    PLUGIN_VERSION = "0.1"

    ZEST_NAME = "zest.sh"

    def _parse_zest_output(self, output):
        if 'FAILED' in output:
            yield {'Summary': self.configuration['zest']['script']['title'],
                   'Severity': 'High',
                   'Description': 'The Zest script raised an assertion.'}

    def do_start(self):
        # Store the script in a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            json.dump(self.configuration['zest']['script'], f)
        self.script_path = f.name
        # Run Zest
        zest_path = self.locate_program(self.ZEST_NAME)
        if zest_path is None:
            raise Exception("Cannot find zest in path")
        self.output = ""
        self.spawn(zest_path, ['-script', self.script_path])

    def do_process_stdout(self, data):
        self.output += data

    def do_process_ended(self, status):
        print self.output
        if self.stopping and status == 9:
            self.report_finish("STOPPED")
        elif status == 0:
            self.callbacks.report_issues(self._parse_zest_output(self.output))
            self.callbacks.report_finish()
        else:
            self.report_finish("FAILED")
