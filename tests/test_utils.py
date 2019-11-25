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

from commoncode.testcase import FileBasedTesting

from tracecode import utils


class TestUtils(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_notice(self):
        expected  = """Generated with TraceCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied. No content created from
TraceCode should be considered or used as legal advice. Consult an Attorney
for any legal advice.
TraceCode is a free software codebase-comparison tool from nexB Inc. and others.
Visit https://github.com/nexB/tracecode-toolkit/ for support and download."""
        result = utils.get_notice()
        print(result)
        assert expected == result

    def test_is_json_path_with_invalid_json_file(self):
        develop_json = self.get_test_loc('utils/invalid/deploy_notjson')
        is_json_file = utils.is_json_path(develop_json)
        assert is_json_file == False

    def test_is_json_path_with_empty_json_file(self):
        develop_json = self.get_test_loc('utils/empty/deploy.json')
        is_json_file = utils.is_json_path(develop_json)
        assert is_json_file == False

    def test_is_json_path_with_valid_json_file(self):
        develop_json = self.get_test_loc('utils/valid/deploy.json')
        is_json_file = utils.is_json_path(develop_json)
        assert is_json_file == True
