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

from scancode.resource import VirtualCodebase

from tracecode import pathutils
from future.backports.test.pystone import TRUE


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

    def append_matched_resource(self, matched_resource):
        if matched_resource:
            should_appended = True
            for existing_resource in self.matched_resources:
                if existing_resource.path == matched_resource.path:
                    if not matched_resource.checksum_matchtype:
                        should_appended = False
            if should_appended:
                self.matched_resources.append(matched_resource)

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
        This will be used by the json dump.
        """
        return self.to_dict()


# TODO: use attr for these data classes
class MatchedResource(object):
    """
    Class to represent the matched resource information.
    """

    def __init__(self, path, matcher_type, confidence, checksum_matchtype=None):
        """
        path: The path matched resource
        matcher: Matcher method type, for example: path match or checksum match etc.
        confident: Match level, for example: high, medium etc.
        """
        self.path = path
        self.matcher = matcher_type
        self.confidence = confidence
        self.checksum_matchtype = checksum_matchtype

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
        self.deploy = deploy

        self.develop_codebase = VirtualCodebase(self.develop)
        self.deploy_codebase = VirtualCodebase(self.deploy)

        self.deploy_paths = []
        for resource in self.deploy_codebase.walk():
            self.deploy_paths.append(resource.path)

        self.develop_paths = []
        for resource in self.develop_codebase.walk():
            self.develop_paths.append(resource.path)

        self.options = options
        self.errors = []

        # mapping of {development resource path: MatchedResource}
        # FIXME: do we really need an OrderedDict?
        self.analysed_result = OrderedDict()

        self.compute()

    def compute(self):
        """
        Compute (or re-compute) the analysis, and store results.
        """
        self.checksum_match()
        # TODO: do we really want to do a path match if we had a checksum
        # match?
        self.path_match()

    def path_match(self):
        """
        Path matching for the develop and deploy resources.
        """
        for resource in self.develop_codebase.walk():
            path = resource.path

            trace_resource = self.create_or_get_traceresource_by_resource(
                resource)

            for matched_path in match_paths(path, self.deploy_paths):
                matched_resource = MatchedResource(
                    matched_path, PATH_MATCH, HIGH_CONFIDENCE)
                trace_resource.matched_resources.append(matched_resource)

            if trace_resource.matched_resources:
                path = trace_resource.resource.path
                self.analysed_result[path] = trace_resource

    def checksum_match(self):
        """
        Compare the sha1 and md5 of the develop and deploy resources, and get
        the matched path which has the same checksum between develop and deploy
        resources

        Note that sha1 and md5 matching is not a AND condition but a OR
        condition, which means any of them is matched will be counted in.
        """
        checksums = ['sha1',  'md5']

        for checksumtype in checksums:
            deployed_path_by_checksum = get_checksum_index(
                self.deploy_codebase, checksumtype)

            for resource in self.develop_codebase.walk():
                resource_checksum = getattr(resource, checksumtype)
                if not resource_checksum:
                    continue

                trace_resource = self.create_or_get_traceresource_by_resource(
                    resource)
                deployed_path = deployed_path_by_checksum.get(
                    resource_checksum)
                if not deployed_path:
                    continue

                matched_resource = MatchedResource(
                    deployed_path, CHECKSUM_MATCH, EXACT_CONFIDENCE, checksumtype)
                trace_resource.append_matched_resource(matched_resource)
                self.analysed_result[resource.path] = trace_resource

    def create_or_get_traceresource_by_resource(self, resource):
        """
         Create a TracecodeResource object based on the passing resource or
         return an existing one by querying with the path of the resource
        """
        path = resource.path
        if self.analysed_result.get(path):
            trace_resource = self.analysed_result.get(path)
        else:
            trace_resource = TracecodeResource(resource)
            self.analysed_result[path] = trace_resource
        return trace_resource

    def add_matched_resource_to_result(self, trace_resource):
        """
        Add the matched resource to the analysed_result.
        If the trace_resource has the matched resource, append to the result
        stored for the class.
        """
        if trace_resource.matched_resources:
            path = trace_resource.resource.path
            self.analysed_result[path] = trace_resource


def get_checksum_index(codebase, checksum='sha1'):
    """
    Return a mapping index of {checksum: path} for a `codebase`.
    """
    # FIXME: what if you have multiple times the same checksum on different files?
    # IMHO you should use a defaultdict(list) instead

    # TODO: we could also handle empty SHA1... BUT that should be something
    # dealt with by Scancode instead
    paths_by_checksum = {}

    for resource in codebase.walk():
        resource_checksum = getattr(resource, checksum)
        if not resource_checksum:
            continue
        paths_by_checksum[resource_checksum] = resource.path
    return paths_by_checksum


def remove_file_suffix(path):
    """
    Remove the deployment/develop file prefix in the path, for example, the develop of java is .java and the deployment is .class.
    This is to match if the file name of the path has a prefix like .java, and the deploy path may have the prefix like .class,
    in this case, it should be matching.
    For example, passing
    /home/test/src/test.java to the function
    will return
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
