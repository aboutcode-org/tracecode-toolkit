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


from __future__ import print_function
from __future__ import absolute_import


from collections import defaultdict
from collections import OrderedDict

import attr
from scancode.resource import Resource
from scancode.resource import VirtualCodebase
from scancode.resource import to_decoded_posix_path

from tracecode import pathutils
from tracecode import utils

# Tracing flags
TRACE = False
TRACE_DEEP = False


PATH_MATCH = 'path match'
CHECKSUM_MATCH = 'checksum match'
EXACT_CONFIDENCE = 'perfect'
HIGH_CONFIDENCE = 'high'
MEDIUM_CONFIDENCE = 'medium'
LOW_CONFIDENCE = 'low'


class TracecodeResource(object):
    """Wrapper class to contain resource and matched resources information.
    """

    def __init__(self, resource):
        self.resource = resource
        self.matched_resources = []

    def to_dict(self):
        res = self.resource.to_dict()
        resources_result = []
        if self.matched_resources:
            for resource in self.matched_resources:
                resources_result.append(resource.to_dict())
        res['deployed_to'] = resources_result
        return res

    def _asdict(self):
        """
        Return dictionary format of the object for JSON serialization.
        """
        return self.to_dict()


class MatchedResource(object):
    """Class to represent the matched resource information.
    """

    def __init__(self, path, matcher_type, confidence):
        self.path = path
        self.matcher = matcher_type
        self.confidence = confidence

    def to_dict(self):
        res = OrderedDict()
        res['path'] = self.path
        res['matcher'] = self.matcher
        res['confidence'] = self.confidence
        return res


class DeploymentAnalysis(object):
    """
    A DeploymentAnalysis holds development and deployment codebases and computes
    how files on each side are related using various matching strategies.
    """

    def __init__(self, develop, deploy,  options):
        self.develop = develop
        self.develop_paths = []
        #self.develop_paths = utils.get_paths_set_from_json(self.develop)
        self.develop_codebase = VirtualCodebase(self.develop)

        self.deploy = deploy
        self.deploy_paths = []
        #self.deploy_paths = utils.get_paths_set_from_json(self.deploy)
        self.deploy_codebase = VirtualCodebase(self.deploy)

        for resource in self.deploy_codebase.walk():
            self.deploy_paths.append(resource.path)

        for resource in self.develop_codebase.walk():
            self.develop_paths.append(resource.path)

        self.options = options
        self.errors = []
        self.analysed_result = OrderedDict()

        self.compute()

    def compute(self):
        """
        Compute (or re-compute) the analysis, return and store results.
        """
        self.checksum_match()
        self.path_match()

    def create_or_get_tracecoderesource(self, resource):
        """
         Create a TracecodeResource object based on the passing resource or return an existing one by query with the path of the resource
        """
        path = resource.path
        if self.analysed_result.get(path):
            trace_resource = self.analysed_result.get(path)
        else:
            trace_resource = TracecodeResource(resource)
            self.analysed_result[path] = trace_resource
        return trace_resource

    def path_match(self):
        """
        Path matching for the develop and deploy resources.
        """
        for resource in self.develop_codebase.walk():
            path = resource.path

            trace_resource = self.create_or_get_tracecoderesource(resource)

            for matched_path in match_paths(path, self.deploy_paths):
                matched_resource = MatchedResource(
                    matched_path, PATH_MATCH, HIGH_CONFIDENCE)
                trace_resource.matched_resources.append(matched_resource)

            if trace_resource.matched_resources:
                self.analysed_result[path] = trace_resource

    def checksum_match(self):
        """
        Compare the sha1 and md5 of the develop and deploy resources, and get the matched path which has the same checksum between develop and deploy resources
        """
        deploy_checksum_map = OrderedDict()
        for resource in self.deploy_codebase.walk():
            sha1 = resource.sha1
            md5 = resource.md5
            path = resource.path
            if sha1:
                deploy_checksum_map[sha1] = path
            if md5:
                deploy_checksum_map[md5] = path

        for resource in self.develop_codebase.walk():
            sha1 = resource.sha1
            md5 = resource.md5
            path = resource.path

            trace_resource = self.create_or_get_tracecoderesource(resource)
            matched_path = deploy_checksum_map.get(sha1)
            if not matched_path:
                # If sha1 is empty or not matched, try md5
                matched_path = deploy_checksum_map.get(md5)
            if matched_path:
                matched_resource = MatchedResource(
                    matched_path, CHECKSUM_MATCH, EXACT_CONFIDENCE)
                trace_resource.matched_resources.append(matched_resource)
            if trace_resource.matched_resources:
                self.analysed_result[path] = trace_resource


def remove_file_suffix(path):
    """
    Remove the file prefix in the path.
    This is to match if the source has prefix like .java, and the deploy has the prefix like .class
    For example, passing
    /home/test/src/test.java
    will be returning
    /home/test/src/test
    """
    if path.endswith(('.java', '.class', '.c', '.cpp' '.o', '.exe', '.py', '.pyc')):
        return path.rsplit('.', 1)[0]
    return path


def match_paths(path1, paths2):
    """
    Given a single path1 and a sequences of paths paths2, match path1 with paths in
    paths2 using a common suffix. Yield a sequences of the top matched paths from path2
    """
    cp1 = defaultdict(set)

    path1_remove_filesuffix = remove_file_suffix(path1)
    for p2 in paths2:
        path2_remove_filesuffix = remove_file_suffix(p2)
        cmn, lgth = pathutils.common_path_suffix(
            path1_remove_filesuffix, path2_remove_filesuffix)
        if cmn:
            cp1[lgth].add(p2)

    if cp1:
        tops = cp1[max(cp1)]
        # do not keep multiple matches of len 1: these are filename matches
        # and are too weak to be valid in most cases
        if not(max(cp1) == 1 and len(tops) > 1):
            for top in tops:
                yield top
