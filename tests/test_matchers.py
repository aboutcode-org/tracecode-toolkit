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

from collections import OrderedDict
import os.path

from scancode.resource import VirtualCodebase

from tracecode.cli import write_json
from tracecode.matchers import DeploymentAnalysis
from tracecode.matchers import get_checksum_index
from tracecode.matchers import match_paths
from tracecode.matchers import remove_file_suffix

from commoncode.testcase import FileBasedTesting
from testing_utils import check_json_scan


class TestMatchers(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_remove_file_suffix(self):
        path1 = '/home/test/src/com/nexb/plugin/ui/core.java'
        result = remove_file_suffix(path1)
        assert result == '/home/test/src/com/nexb/plugin/ui/core'

    def test_remove_file_suffix2(self):
        path1 = '/home/test/src/com/nexb/plugin/ui/readme'
        result = remove_file_suffix(path1)
        assert result == '/home/test/src/com/nexb/plugin/ui/readme'

    def test_remove_file_suffix3(self):
        path1 = '/home/test/src/com/nexb/plugin/ui.test/readme'
        result = remove_file_suffix(path1)
        assert result == '/home/test/src/com/nexb/plugin/ui.test/readme'

    def test_remove_file_suffix4(self):
        path1 = '/home/test/src/com/nexb/plugin/ui.test/test.class'
        result = remove_file_suffix(path1)
        assert result == '/home/test/src/com/nexb/plugin/ui.test/test'

    def test_path_matcher(self):
        path1 = '/home/test/src/com/nexb/plugin/ui/core.java'
        path2 = ['com/nexb/plugin/ui/core.class',
                 'com/nexb/plugin/ui/test.class']
        expected = [u'com/nexb/plugin/ui/core.class']
        result = match_paths(path1, path2)
        assert list(result) == expected

    def test_path_matcher2(self):
        path1 = '/home/test/src/com/nexb/plugin/ui/readme'
        path2 = ['com/nexb/plugin/ui/readme',
                 'com/nexb/plugin/ui/test.class']
        expected = [u'com/nexb/plugin/ui/readme']
        result = match_paths(path1, path2)
        assert list(result) == expected

    def test_get_checksum_index_sha1(self):
        develop_json = self.get_test_loc('matchers/checksumindex/develop.json')
        codebase = VirtualCodebase(develop_json)
        result = get_checksum_index(codebase)
        expected = {u'01ff4b1de0bc6c75c9cca6e46c80c1802d6976d4': [u'samples/screenshot.png'],
                    u'2e07e32c52d607204fad196052d70e3d18fb8636': [u'samples/README']
                    }
        assert expected == result

    def test_get_checksum_index_sha1(self):
        develop_json = self.get_test_loc('matchers/checksumindex/develop.json')
        codebase = VirtualCodebase(develop_json)
        result = get_checksum_index(codebase, 'md5')
        expected = {u'b6ef5a90777147423c98b42a6a25e57a': [u'samples/screenshot.png'],
                    u'effc6856ef85a9250fb1a470792b3f38': [u'samples/README']}
        assert expected == result

    def test_deploymentanalysis_class(self):
        develop_json = self.get_test_loc('matchers/class/develop.json')
        deploy_json = self.get_test_loc('matchers/class/deploy.json')
        expected_file = self.get_test_loc('matchers/class/expected.json')
        da = DeploymentAnalysis(develop_json, deploy_json,  options=OrderedDict([
            ('--develop', develop_json),
            ('--deploy', deploy_json),
        ])
        )
        result_file = self.get_temp_file('json')
        with open(result_file, 'w') as rfile:
            write_json(analysis=da, outfile=rfile)
        check_json_scan(expected_file, result_file, regen=False)
