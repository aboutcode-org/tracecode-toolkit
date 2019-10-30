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

from collections import OrderedDict

import click
import simplejson

from tracecode import __version__
from tracecode import TraceCode
from tracecode.utils import get_notice


def write_json(tracecode, outfile, all_paths=False):
    """
    Using the TraceCode object, create a .json file containing the primary
    information from the Delta objects.  Through a call to utils.deltas(), omit
    all unmodified Delta objects -- identified by a 'score' of 0 -- unless the
    user selects the '-a'/'--all-delta-types' option.
    """
    results = OrderedDict([
        ('tracecode_notice', get_notice()),
        ('tracecode_options', tracecode.options),
        ('tracecode_version', __version__),
        ('tracecode_errors',tracecode.errors),
        ('tracecode_results',tracecode.results),
      
    ])

    simplejson.dump(results, outfile, iterable_as_array=True, indent=2)
    outfile.write('\n')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('TraceCode version ' + __version__)
    ctx.exit()


@click.command()
@click.option('--deploy',required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Path to the "deployed" codebase scan file')
@click.option('--develop', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Path to the "development" codebase scan file')
@click.option('-j', '--json', prompt=False, default='-', type=click.File(mode='wb', lazy=False), help='Path of the .json output file. Use "-" for on screen display.')
@click.help_option('-h', '--help')
@click.option('--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version, help='Show the version and exit.')
def cli(deploy, develop, json):
    """
    Command to accept location of deploy and develop json inputs, run the tracecode scan and return the expected same paths set by comparision of paths.
    """
    options = OrderedDict([
        ('--deploy', deploy),
        ('--develop', develop),
    ])
    tracecode= TraceCode(deploy, develop, options)
    write_json(tracecode, json)

