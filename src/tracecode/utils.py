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

import os


def get_notice():
    """
    Retrieve the notice text from the NOTICE file for display in the JSON output.
    """
    notice_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'NOTICE')
    notice_text = open(notice_path).read()

    delimiter = '\n\n\n'
    [notice_text, extra_notice_text] = notice_text.split(delimiter, 1)
    extra_notice_text = delimiter + extra_notice_text

    delimiter = '\n\n  '
    [notice_text, acknowledgment_text] = notice_text.split(delimiter, 1)
    acknowledgment_text = delimiter + acknowledgment_text

    notice = acknowledgment_text.strip().replace('  ', '')

    return notice
