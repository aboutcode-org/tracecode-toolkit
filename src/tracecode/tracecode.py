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

"""
TraceCode is a tool to analyze the graph of file transformations from a
traced command, typically a build command.
"""

from __future__ import print_function, absolute_import

import logging
import re

from tracecode import pathutils

# use a large compiled regex cache to avoid having to cache regex compilations
re._MAXCACHE = 1000000

__version__ = '0.8.0'


logger = logging.getLogger('tracecode')


def match_paths(paths1, paths2):
    """
    Given two sequences of paths, match every paths in paths1 with paths in
    paths2 using a common suffix. Yield a sequences of the top match tuples
    (p1, p2,)
    """
    from collections import defaultdict
    for p1 in paths1:
        cp1 = defaultdict(set)

        for p2 in paths2:
            cmn, lgth = pathutils.common_path_suffix(p1, p2)
            if cmn:
                cp1[lgth].add(p2)

        if cp1:
            tops = cp1[max(cp1)]
            # do not keep multiple matches of len 1: these are filename matches
            # and are too weak to be valid in most cases
            if not(max(cp1) == 1 and len(tops) > 1):
                for top in tops:
                    yield p1, top
