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
from commoncode.datautils import String
from scancode.resource import VirtualCodebase

from tracecode import pathutils


PATH_MATCH = 'path match'
CHECKSUM_MATCH = 'checksum match'

EXACT_CONFIDENCE = 'perfect'
HIGH_CONFIDENCE = 'high'
MEDIUM_CONFIDENCE = 'medium'
LOW_CONFIDENCE = 'low'


class TracecodeResource(object):
    """
    Wrapper class to contain resource and matched resources information.
    """

    def __init__(self, resource):
        # The develop resource
        self.resource = resource
        # The targeted deployed resources
        self.deployed_resources = []

    def add_deployed_resource(self, matched_resource):
        """
        Append the matched_resource, if the checksum result with the same path is already in the result, skip it.
        """
        if matched_resource:
            should_append = True
            for existing_resource in self.deployed_resources:
                # If the checksum is matched,  skip other types of match.
                if existing_resource.path == matched_resource.path and existing_resource.matcher == CHECKSUM_MATCH:
                    should_append = False
            if should_append:
                self.deployed_resources.append(matched_resource)

    def to_dict(self):
        res = self.resource.to_dict()
        resources_result = []
        if self.deployed_resources:
            for deployed_resource in self.deployed_resources:
                resources_result.append(deployed_resource.to_dict())
        res['deployed_to'] = resources_result
        return res

    def _asdict(self):
        """
        Return dictionary format of the object for JSON serialization.
        This will be used by the json dump.
        """
        return self.to_dict()


@attr.s(slots=True)
class MatchedResource(object):
    """
    Class to represent the matched resource information.
    """
    path = String(help='The path matched resource')
    matcher = String(
        help='Matcher method type, for example: path match or checksum match etc.')
    confidence = String(
        help='Match level, for example: high, medium etc.')
    checksum_matchtype = String(
        default=None, help='Checksum type such as sha1, md5 etc.')

    def to_dict(self):
        res = OrderedDict()
        res['path'] = self.path
        res['matcher'] = self.matcher
        res['confidence'] = self.confidence
        if self.checksum_matchtype:
            res['checksum_matchtype'] = self.checksum_matchtype
        return res


class DeploymentAnalysis(object):
    """
    A DeploymentAnalysis holds development and deployment codebases and computes
    how files on each side are related using various matching strategies.
    """

    def __init__(self, develop_json_location, deploy_json_location,  options):
        """
        develop_json_location: The json location of the develop resources.
        deploy_json_location: The json location of the deploy resources.
        options: The cli options.
        """
        self.develop = develop_json_location
        self.deploy = deploy_json_location

        self.develop_codebase = VirtualCodebase(self.develop)
        self.deploy_codebase = VirtualCodebase(self.deploy)

        self.deploy_paths = [
            resource.path for resource in self.deploy_codebase.walk()]

        self.develop_paths = [
            resource.path for resource in self.develop_codebase.walk()]

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
        # The path match should be after checksum match, since if checksum is
        # matched, the result of path match will be ignored
        self.path_match()

    def path_match(self):
        """
        Path matching for the develop and deploy resources.
        """
        for develop_resource in self.develop_codebase.walk():
            develop_path = develop_resource.path

            for matched_deploy_path in match_paths(develop_path, self.deploy_paths):
                matched_deploy_resource = MatchedResource(
                    matched_deploy_path, PATH_MATCH, HIGH_CONFIDENCE)
                trace_resource_develop_based = self.create_or_get_traceresource_by_resource(
                    develop_resource)
                trace_resource_develop_based.add_deployed_resource(
                    matched_deploy_resource)

    def checksum_match(self):
        """
        Compare the sha1 and md5 of the develop and deploy resources, and get
        the matched paths list which has the same checksum between develop and deploy
        resources, using the paths list, create matched resource and add it the result.
        """
        checksums = ['sha1',  'md5']

        for checksumtype in checksums:
            deploy_paths_by_checksum = get_checksum_index(
                self.deploy_codebase, checksumtype)

            for develop_resource in self.develop_codebase.walk():
                develop_resource_checksum = getattr(
                    develop_resource, checksumtype)
                if not develop_resource_checksum:
                    continue

                deploy_paths = deploy_paths_by_checksum.get(
                    develop_resource_checksum)
                if not deploy_paths:
                    continue   # If the checksum is not found in the index, skip

                for deploy_path in deploy_paths:
                    matched_deploy_resource = MatchedResource(
                        deploy_path, CHECKSUM_MATCH, EXACT_CONFIDENCE, checksumtype)
                    trace_resource_develop_based = self.create_or_get_traceresource_by_resource(
                        develop_resource)
                    trace_resource_develop_based.add_deployed_resource(
                        matched_deploy_resource)

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
        if trace_resource.deployed_resources:
            self.analysed_result[trace_resource.resource.path] = trace_resource


def get_checksum_index(codebase, checksum='sha1'):
    """
    Return a mapping index of {checksum: [path,...]} for a `codebase`.
    """
    # TODO: we could also handle empty SHA1... BUT that should be something
    # dealt with by Scancode instead
    paths_by_checksum = {}

    for resource in codebase.walk():
        resource_checksum = getattr(resource, checksum)
        if not resource_checksum:
            continue
        paths = paths_by_checksum.get(resource_checksum)
        if paths:
            paths_by_checksum.get(resource_checksum).append(resource.path)
        else:
            paths_by_checksum[resource_checksum] = [resource.path]
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
