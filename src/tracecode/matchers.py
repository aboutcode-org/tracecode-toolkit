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
import copy
import sys

import attr
from scancode.resource import Resource
from scancode.resource import VirtualCodebase
from scancode.resource import to_decoded_posix_path
from six import string_types

from tracecode import pathutils
from tracecode import utils

# Tracing flags
TRACE = False
TRACE_DEEP = False


def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP:
    import logging
    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, string_types) and a or repr(a) for a in args))


class TracecodeResource(object):

    def __init__(self, resource):
        self.resource = resource
        self.matched_resources = []

    def to_dict(self):
        res = self.resource.to_dict()
        resources_result = []
        if self.matched_resources:
            for resource in self.matched_resources:
                resources_result.append(resource.to_dict())
        res['matched_resources'] = resources_result
        return res

    def _asdict(self):
        """
        Return dictionary format of the object for JSON serialization.
        """
        return self.to_dict()


class MatchedResource(object):

    def __init__(self, path):
        self.path = path

    def to_dict(self):
        res = OrderedDict()
        res['path'] = self.path
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

        self.options = options
        self.errors = []
        self.analysed_result = []

        self.compute()
        
    def compute(self):
        """
        Compute (or re-compute) the analysis, return and store results.
        """
        for resource in self.deploy_codebase.walk():
            self.deploy_paths.append(resource.path)
        for resource in self.develop_codebase.walk():
            self.develop_paths.append(resource.path)
        
        for resource in self.develop_codebase.walk():
            path  = resource.path
            trace_resource = TracecodeResource(resource)
            for matched_path in match_paths(path, self.deploy_paths):
                matched_resource = MatchedResource(matched_path)
                trace_resource.matched_resources.append(matched_resource)
            if trace_resource.matched_resources:
                self.analysed_result.append(trace_resource)


def match_paths(paths1, paths2):
    """
    Given two sequences of paths, match every paths in paths1 with paths in
    paths2 using a common suffix. Yield a sequences of the top matched path
    """
    cp1 = defaultdict(set)

    for p2 in paths2:
        cmn, lgth = pathutils.common_path_suffix(paths1, p2)
        if cmn:
            cp1[lgth].add(p2)

    if cp1:
        tops = cp1[max(cp1)]
        # do not keep multiple matches of len 1: these are filename matches
        # and are too weak to be valid in most cases
        if not(max(cp1) == 1 and len(tops) > 1):
            for top in tops:
                yield  top
