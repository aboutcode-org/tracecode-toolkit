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
click.disable_unicode_literals_warning = True
from commoncode import filetype
from commoncode import fileutils
import simplejson

from tracecode import __version__
from tracecode import matchers
from tracecode.utils import get_notice


def write_json(analysis, outfile):
    """
    Write the data from the `analysis` DeploymentAnalysis as JSON to `outfile`.
    """
    results = OrderedDict([
        ('tracecode_notice', get_notice()),
        ('tracecode_options', analysis.options),
        ('tracecode_version', __version__),
        ('tracecode_errors', analysis.errors),
        ('tracecode_results', analysis.analysed_result),

    ])

    simplejson.dump(results, outfile, iterable_as_array=True, indent=2)
    outfile.write('\n')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('TraceCode version ' + __version__)
    ctx.exit()


@click.command()
@click.option('--deploy', required=True, prompt=False,
              type=click.Path(exists=True, readable=True),
              help='Path to the "deployed" codebase scan file')
@click.option('--develop', required=True, prompt=False,
              type=click.Path(exists=True, readable=True),
              help='Path to the "development" codebase scan file')
@click.option('-j', '--json', prompt=False, default='-',
              type=click.File(mode='wb', lazy=False),
              help='Path of the .json output file. Use "-" for on screen display.')
@click.help_option('-h', '--help')
@click.option('--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version, help='Show the version and exit.')
def cli(develop, deploy, json):
    """
    Command to accept location of deploy and develop json inputs, run the
    tracecode scan and return the expected same paths set by comparison of paths.
    """
    options = OrderedDict([
        ('--develop', develop),
        ('--deploy', deploy),
    ])

    # FIXME: I am not we care about the paths having a .json extension.
    if not is_json_path(develop):
        click.echo('Develop path is not a json file:' + develop)
        return
    if not is_json_path(deploy):
        click.echo('Deploy path is not a json file: ' + deploy)
        return

    analysis = matchers.DeploymentAnalysis(develop=develop, deploy=deploy, options=options)
    write_json(analysis=analysis, outfile=json)


def is_json_path(location):
    """Test if the input location file is a valid json file or not.
    """
    if filetype.is_file(location):
        try:
            with open(location) as jsonfile:
                result = simplejson.load(jsonfile)
                if result:
                    return True
        except:
            return False
    return False

