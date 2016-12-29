#!/usr/bin/env python
from __future__ import absolute_import

import boto3
import click
from click import ClickException
import json
import os
import platform
import sys
from base64 import b64decode
from botocore.exceptions import ClientError
from lambkin.aws import get_role_arn, get_event_rule_arn
from lambkin.aws import get_function_arn, get_region
from lambkin.runtime import get_sane_runtime, get_file_extension_for_runtime
from lambkin.runtime import get_language_name_for_runtime
from lambkin.template import render_template
from lambkin.ux import say
from lambkin.virtualenv import create_virtualenv, run_in_virtualenv
from lambkin.zip import create_zip
import lambkin.metadata as metadata
from subprocess import check_output, CalledProcessError, STDOUT

VERSION = '0.3.0'

lmbda = boto3.client('lambda', region_name=get_region())


@click.command(help='Make a new Lambda function from a basic template.')
@click.argument('function')
@click.option('--runtime', help='The language runtime to use. eg. "python2.7".')
def create(function, runtime):
    runtime = get_sane_runtime(runtime)

    ext = get_file_extension_for_runtime(runtime)
    func_dir = function
    func_file = os.path.join(func_dir, '%s.%s' % (function, ext))

    for path in (func_dir, func_file):
        if os.path.exists(path):
            raise ClickException('Path "%s" already exists.' % path)

    os.mkdir(func_dir)

    template_name = get_language_name_for_runtime(runtime)
    render_template(template_name, function,
                    output_filename="%s.%s" % (function, ext))
    if get_language_name_for_runtime(runtime) == 'python':
        create_virtualenv(function)
        render_template('requirements', function, output_filename='requirements.txt')
        render_template('gitignore-python', function, output_filename='.gitignore')
    else:
        render_template('makefile', function, output_filename='Makefile')
        render_template('gitignore', function, output_filename='.gitignore')

    our_metadata = {
        'function': function,
        'runtime': runtime,
        'language': get_language_name_for_runtime(runtime),
        'timeout': metadata.get('timeout')
    }
    metadata.write(subdirectory=function, **our_metadata)

    say('%s created as %s' % (function, func_file))


def get_published_function_names():
    """Return the names of all published functions."""
    return [f['FunctionName'] for f in lmbda.list_functions()['Functions']]


@click.command(name='list-published',
               help='List published Lambda functions.')
def list_published():
    for f in lmbda.list_functions()['Functions']:
        print f['FunctionName']


@click.command(help="Run the build process for a function.")
def build():
    runtime = metadata.get('runtime')
    language = get_language_name_for_runtime(runtime)
    if language == 'python':
        # Use virtualenv and pip
        if not os.path.isfile('venv'):
            create_virtualenv('.')
        print run_in_virtualenv('pip install -r requirements.txt')
    else:
        # Fall back to a Makefile.
        try:
            make_log = check_output(['make'], stderr=STDOUT)
            for line in make_log.rstrip().split("\n"):
                say(line)
        except CalledProcessError as e:
            for line in e.output.rstrip().split("\n"):
                say(line)
            raise ClickException('make failure')


@click.command(help='Publish a function to Lambda.')
@click.option('--description', help="Descriptive text in AWS Lamda.")
@click.option('--timeout', type=click.IntRange(min=1, max=300),
              help="Maximum time the function can run, in seconds.")
@click.option('--memory', type=click.IntRange(min=128, max=1536),
              help="Memory allocated to the function, in MiB.")
@click.option('--role', help="Lambda execution role. Default: lambda_basic_execution")
@click.option('--zip-file-path', help="Name of zip file that lambkin creates. Default: /tmp/lambkin-publish-<function>.zip.")
@click.option('--zip-file-only', is_flag=True, help="Produce zip file and exit without publishing.")
def publish(description, timeout, memory, role, zip_file_only, zip_file_path):
    runtime = metadata.get('runtime')
    function = metadata.get('function')

    if description:
        metadata.update(description=description)
    else:
        try:
            description = metadata.get('description')
        except KeyError:
            raise ClickException('Please provide a description with "--description"')

    if timeout:
        metadata.update(timeout=timeout)
    else:
        timeout = metadata.get('timeout')

    if memory:
        metadata.update(memory=memory)
    else:
        memory = metadata.get('memory')

    if role:
        metadata.update(role=role)
    else:
        role = metadata.get('role')

    zip_data = open(create_zip(zip_file_path)).read()

    if zip_file_only:
        return

    if function in get_published_function_names():
        # Push the latest code to the existing function in Lambda.
        update_code_response = lmbda.update_function_code(
            FunctionName=function,
            ZipFile=zip_data,
            Publish=True)

        # Update any settings for the function too.
        final_response = lmbda.update_function_configuration(
            FunctionName=function,
            Description=description,
            Role=get_role_arn(role),
            Timeout=timeout,
            MemorySize=memory)
        say('%s updated in Lambda' % function)
    else:  # we need to explictly create the function in AWS.
        final_response = lmbda.create_function(
            FunctionName=function,
            Description=description,
            Runtime=runtime,
            Role=get_role_arn(role),
            Handler='%s.handler' % function,
            Code={'ZipFile': zip_data},
            Timeout=timeout,
            MemorySize=memory)
        say('%s created in Lambda' % function)
    print json.dumps(final_response, sort_keys=True, indent=2)


@click.command(help='Run a published function.')
@click.option('--function', help="Defaults to the function in the current dir.")
def run(function):
    if not function:
        function = metadata.get('function')
    result = lmbda.invoke(FunctionName=function, LogType='Tail')
    log = b64decode(result['LogResult']).rstrip().split("\n")
    for line in log:
        say(line)
    print result['Payload'].read()


@click.command(help='Remove a function from Lambda.')
@click.option('--function', help="Defaults to the function in the current dir.")
def unpublish(function):
    if not function:
        function = metadata.get('function')
    lmbda.delete_function(FunctionName=function)
    say('%s unpublished' % (function))


@click.command(help='Schedule a function to run regularly.')
@click.option('--function', help="Defaults to the function in the current dir.")
@click.option('--rate', help='Execution rate. Like "6 minutes", or "1 day".')
@click.option('--cron', help='Cron schedule. Like "0 8 1 * ? *".')
def schedule(function, rate, cron):
    if not function:
        function = metadata.get('function')
    events = boto3.client('events', region_name=get_region())

    if (rate and cron):
        raise ClickException(
            'Please use either "--rate" or "--cron", not both.')
    if rate:
        schedule_expression = 'rate(%s)' % rate
    elif cron:
        schedule_expression = 'cron(%s)' % cron
    else:
        raise ClickException('Please provide "--rate" or "--cron".')

    try:
        lmbda.add_permission(
            FunctionName=function,
            StatementId='lambkin-allow-cloudwatch-invoke-%s' % function,
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=get_event_rule_arn('lambkin-cron-%s' % function),
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            # The rule is already there. Carry on!
            pass
        else:
            raise e

    events.put_rule(
        Name='lambkin-cron-%s' % function,
        ScheduleExpression=schedule_expression,
        State='ENABLED',
        Description='Lambkin cron for %s Lambda function' % function,
    )

    response = events.put_targets(
        Rule='lambkin-cron-%s' % function,
        Targets=[{
            'Id': function,
            'Arn': get_function_arn(function),
        }]
    )

    print json.dumps(response, sort_keys=True, indent=2)


def main():
    if platform.system() == 'Windows':
        print "Lambkin doesn't run on Windows yet. Sorry."
        sys.exit(1)

    @click.group(invoke_without_command=True, no_args_is_help=True)
    @click.pass_context
    @click.option('--version', help='Show the version.', is_flag=True)
    def cli(ctx, version):
        if ctx.invoked_subcommand is None and version:
            click.echo(VERSION)

    subcommands = [create, list_published, build, publish, run, schedule,
                   unpublish]
    for cmd in subcommands:
        cli.add_command(cmd)
    cli()


if __name__ == '__main__':
    main()
