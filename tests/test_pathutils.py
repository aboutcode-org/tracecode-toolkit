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

import unittest

from tracecode import pathutils


class TestPathUtils(unittest.TestCase):

    def test_common_path_prefix1(self):
        test = pathutils.common_path_prefix('/a/b/c', '/a/b/c')
        assert ('a/b/c', 3) == test

    def test_common_path_prefix2(self):
        test = pathutils.common_path_prefix('/a/b/c', '/a/b')
        assert ('a/b', 2) == test

    def test_common_path_prefix3(self):
        test = pathutils.common_path_prefix('/a/b', '/a/b/c')
        assert ('a/b', 2) == test

    def test_common_path_prefix4(self):
        test = pathutils.common_path_prefix('/a', '/a')
        assert ('a', 1) == test

    def test_common_path_prefix_path_root(self):
        test = pathutils.common_path_prefix('/a/b/c', '/')
        assert (None, 0) == test

    def test_common_path_prefix_root_path(self):
        test = pathutils.common_path_prefix('/', '/a/b/c')
        assert (None, 0) == test

    def test_common_path_prefix_root_root(self):
        test = pathutils.common_path_prefix('/', '/')
        assert (None, 0) == test

    def test_common_path_prefix_path_elements_are_similar(self):
        test = pathutils.common_path_prefix('/a/b/c', '/a/b/d')
        assert ('a/b', 2) == test

    def test_common_path_prefix_no_match(self):
        test = pathutils.common_path_prefix('/abc/d', '/abe/f')
        assert (None, 0) == test

    def test_common_path_prefix_ignore_training_slashes(self):
        test = pathutils.common_path_prefix('/a/b/c/', '/a/b/c/')
        assert ('a/b/c', 3) == test

    def test_common_path_prefix8(self):
        test = pathutils.common_path_prefix('/a/b/c/', '/a/b')
        assert ('a/b', 2) == test

    def test_common_path_prefix10(self):
        test = pathutils.common_path_prefix('/a/b/c.txt',
                                                     '/a/b/b.txt')
        assert ('a/b', 2) == test

    def test_common_path_prefix11(self):
        test = pathutils.common_path_prefix('/a/b/c.txt', '/a/b.txt')
        assert ('a', 1) == test

    def test_common_path_prefix12(self):
        test = pathutils.common_path_prefix('/a/c/e/x.txt',
                                                     '/a/d/a.txt')
        assert ('a', 1) == test

    def test_common_path_prefix13(self):
        test = pathutils.common_path_prefix('/a/c/e/x.txt', '/a/d/')
        assert ('a', 1) == test

    def test_common_path_prefix14(self):
        test = pathutils.common_path_prefix('/a/c/e/', '/a/d/')
        assert ('a', 1) == test

    def test_common_path_prefix15(self):
        test = pathutils.common_path_prefix('/a/c/e/', '/a/c/a.txt')
        assert ('a/c', 2) == test

    def test_common_path_prefix16(self):
        test = pathutils.common_path_prefix('/a/c/e/', '/a/c/f/')
        assert ('a/c', 2) == test

    def test_common_path_prefix17(self):
        test = pathutils.common_path_prefix('/a/a.txt', '/a/b.txt/')
        assert ('a', 1) == test

    def test_common_path_prefix18(self):
        test = pathutils.common_path_prefix('/a/c/', '/a/')
        assert ('a', 1) == test

    def test_common_path_prefix19(self):
        test = pathutils.common_path_prefix('/a/c.txt', '/a/')
        assert ('a', 1) == test

    def test_common_path_prefix20(self):
        test = pathutils.common_path_prefix('/a/c/', '/a/d/')
        assert ('a', 1) == test

    def test_common_path_suffix(self):
        test = pathutils.common_path_suffix('/a/b/c', '/a/b/c')
        assert ('a/b/c', 3) == test

    def test_common_path_suffix_absolute_relative(self):
        test = pathutils.common_path_suffix('a/b/c', '/a/b/c')
        assert ('a/b/c', 3) == test

    def test_common_path_suffix_find_subpath(self):
        test = pathutils.common_path_suffix('/z/b/c', '/a/b/c')
        assert ('b/c', 2) == test

    def test_common_path_suffix_handles_relative_path(self):
        test = pathutils.common_path_suffix('a/b', 'a/b')
        assert ('a/b', 2) == test

    def test_common_path_suffix_handles_relative_subpath(self):
        test = pathutils.common_path_suffix('zsds/adsds/a/b/b/c',
                                                     'a//a/d//b/c')
        assert ('b/c', 2) == test

    def test_common_path_suffix_ignore_and_strip_trailing_slash(self):
        test = pathutils.common_path_suffix('zsds/adsds/a/b/b/c/',
                                                     'a//a/d//b/c/')
        assert ('b/c', 2) == test

    def test_common_path_suffix_return_None_if_no_common_suffix(self):
        test = pathutils.common_path_suffix('/a/b/c', '/')
        assert (None, 0) == test

    def test_common_path_suffix_return_None_if_no_common_suffix2(self):
        test = pathutils.common_path_suffix('/', '/a/b/c')
        assert (None, 0) == test

    def test_common_path_suffix_match_only_whole_segments(self):
        # only segments are honored, commonality within segment is ignored
        test = pathutils.common_path_suffix(
            'this/is/aaaa/great/path', 'this/is/aaaaa/great/path')
        assert ('great/path', 2) == test

    def test_common_path_suffix_two_root(self):
        test = pathutils.common_path_suffix('/', '/')
        assert (None, 0) == test

    def test_common_path_suffix_empty_root(self):
        test = pathutils.common_path_suffix('', '/')
        assert (None, 0) == test

    def test_common_path_suffix_root_empty(self):
        test = pathutils.common_path_suffix('/', '')
        assert (None, 0) == test

    def test_common_path_suffix_empty_empty(self):
        test = pathutils.common_path_suffix('', '')
        assert (None, 0) == test
