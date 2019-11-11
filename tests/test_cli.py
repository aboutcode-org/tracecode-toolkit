#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/tracecode-toolkit/
# The TraceCode software is licensed under the Apache License version 2.0.
# Data generated with TraceCode require an acknowledgment.
# TraceCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with TraceCode or any TraceCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with TraceCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  TraceCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  TraceCode is a free and open source software analysis tool from nexB Inc. and others.
#  Visit https://github.com/nexB/tracecode-toolkit/ for support and download.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from testing_utils import check_json_scan
from testing_utils import run_scan_click

from tracecode import cli


class TestCLI(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_cli_with_empty_json(self):
        develop_json = self.get_test_loc('cli/empty/develop.json')
        deploy_json = self.get_test_loc('cli/empty/deploy.json')
        result_file = self.get_temp_file('json')
        args = ['--develop', develop_json, '--deploy',deploy_json, '-j', result_file]
        result = run_scan_click(args)
        expected = 'Develop path is not a json file:'
        assert expected in result.output

    def test_cli_with_regular_json(self):
        develop_json = self.get_test_loc('cli/codebase/develop.json')
        deploy_json = self.get_test_loc('cli/codebase/deploy.json')
        expected_json = self.get_test_loc('cli/codebase/expected.json')

        result_file = self.get_temp_file('json')

        args = ['--develop', develop_json, '--deploy',deploy_json, '-j', result_file]
        run_scan_click(args)

        check_json_scan(expected_json, result_file, regen=True)

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ['--help'])

        assert 'Usage: cli [OPTIONS]' in result.output
        assert 'Command to accept location of deploy and develop json' in result.output
        assert '--version' in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ['--version'])

        assert 'TraceCode version 1.0.0' in result.output

    def test_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, [])

        assert 'Usage: cli [OPTIONS]' in result.output
        assert 'Error: Missing option "--deploy".' in result.output

    def test_cli_not_existing(self):
        develop_json = 'cli/not_existing/not_existing.json'
        deploy_json = 'cli/not_existing/not_existing.json'
        result_file = self.get_temp_file('json')

        args = ['--develop', develop_json, '--deploy',deploy_json,  '-j', result_file]
        result = run_scan_click(args, expected_rc=2)
        expected = 'Error: Invalid value for "--develop": Path "cli/not_existing/not_existing.json" does not exist.'
        assert expected in result.output

    def test_cli_with_invalid_json_file(self):
        develop_json = self.get_test_loc('cli/invalid/develop.json')
        deploy_json = self.get_test_loc('cli/invalid/deploy_notjson')
        result_file = self.get_temp_file('json')

        args = ['--develop', develop_json, '--deploy',
                deploy_json, '-j', result_file]
        result = run_scan_click(args)
        assert 'Deploy path is not a json file:' in result.output

    def test_is_json_path_with_invalid_json_file(self):
        develop_json = self.get_test_loc('cli/invalid/deploy_notjson')
        is_json_file = cli.is_json_path(develop_json)
        assert is_json_file == False
    
    def test_is_json_path_with_empty_json_file(self):
        develop_json = self.get_test_loc('cli/empty/deploy.json')
        is_json_file = cli.is_json_path(develop_json)
        assert is_json_file == False
