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


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('tracecode-toolkit').version
except DistributionNotFound:
    # package is not installed ??
    __version__ = '1.0.0'


class TraceCode(object):
    """
    Handle the basic operations on a pair of incoming ScanCode scans (in JSON
    format) and return the same paths from a comparison of the paths in both input
    jsons.
    """
    def __init__(self, deploy, develop, options):
        self.deploy = deploy
        self.develop = develop
        self.options = options
        self.errors = []
        self.results = []
        self._parse()
        
    def _parse(self):
        """
        Parse the deploy and develop json and return a set of same paths.
        """
        from tracecode import tracecode
        from tracecode import conf
        from tracecode import utils
        stgs = conf.BaseSettings()
        sources = utils.get_paths_set_from_json(self.deploy)
        targets = utils.get_paths_set_from_json(self.develop)
        self.results  = list(tracecode.match_paths(sources,targets))
