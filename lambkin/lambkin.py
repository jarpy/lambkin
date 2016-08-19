#!/usr/bin/env python
from __future__ import absolute_import

import boto3
import click
import json
import os
from base64 import b64decode
from botocore.exceptions import ClientError
from lambkin.aws import get_role_arn, get_event_rule_arn
from lambkin.aws import get_function_arn
from lambkin.exceptions import Fatal
from lambkin.runtime import get_sane_runtime, get_file_extension_for_runtime
from lambkin.runtime import get_language_name_for_runtime
from lambkin.template import render_template
from lambkin.ux import say
from lambkin.virtualenv import create_virtualenv, run_in_virtualenv
from lambkin.zip import create_zip
import lambkin.metadata as metadata
from subprocess import check_output, CalledProcessError, STDOUT


lmbda = boto3.client('lambda')


@click.command(help='Make a new Lambda function from a basic template.')
@click.argument('function')
@click.option('--runtime', help='The language runtime to use. eg. "python2.7".')
def create(function, runtime):
    runtime = get_sane_runtime(runtime)

    ext = get_file_extension_for_runtime(runtime)
    func_dir = function                # "functions/funky"
    func_file = '%s/%s.%s' % (func_dir, function, ext)  # "functions/funky/funky.py"

    for path in (func_dir, func_file):
        if os.path.exists(path):
            raise Fatal('Path "%s" already exists.' % path)

    os.mkdir(func_dir)

    template_name = get_language_name_for_runtime(runtime)
    render_template(template_name, function,
                    output_filename="%s.%s" % (function, ext))
    render_template('gitignore', function, output_filename='.gitignore')
    if get_language_name_for_runtime(runtime) == 'python':
        create_virtualenv(function)
        render_template('requirements', function, output_filename='requirements.txt')
    else:
        render_template('makefile', function, output_filename='Makefile')

    our_metadata = {
        'function': function,
        'runtime': runtime,
        'language': get_language_name_for_runtime(runtime)
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
    runtime = metadata.read()['runtime']
    language = get_language_name_for_runtime(runtime)
    if language == 'python':
        # Use virtualenv and pip
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
            raise Fatal('make failure')


@click.command(help='Publish a function to Lambda.')
@click.option('--description', help="Descriptive text in AWS Lamda.")
@click.option('--timeout', type=click.IntRange(min=1, max=300),
              default=60, help="Maximum time the function can run, in seconds.")
@click.option('--role', default='lambda-basic-execution')
def publish(description, timeout, role):
    runtime = metadata.read()['runtime']
    function = metadata.read()['function']
    if description:
        metadata.update(description=description)
    else:
        try:
            description = metadata.read()['description']
        except KeyError:
            raise Fatal('Please provide a description with "--description"')

    # zip_file = make_archive('/tmp/lambda-publish', 'zip', code_dir)
    zip_data = open(create_zip()).read()

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
            Timeout=timeout)
        say('%s updated in Lambda' % function)
    else:  # we need to explictly create the function in AWS.
        final_response = lmbda.create_function(
            FunctionName=function,
            Description=description,
            Runtime=runtime,
            Role=get_role_arn(role),
            Handler='%s.handler' % function,
            Code={'ZipFile': zip_data},
            Timeout=timeout)
        say('%s created in Lambda' % function)
    print json.dumps(final_response, sort_keys=True, indent=2)


@click.command(help='Run a published function.')
@click.option('--function', help="Defaults to the function in the current dir.")
def run(function):
    if not function:
        function = metadata.read()['function']
    result = lmbda.invoke(FunctionName=function, LogType='Tail')
    log = b64decode(result['LogResult']).rstrip().split("\n")
    for line in log:
        say(line)
    print result['Payload'].read()


@click.command(help='Remove a function from Lambda.')
@click.option('--function', help="Defaults to the function in the current dir.")
def unpublish(function):
    if not function:
        function = metadata.read()['function']
    lmbda.delete_function(FunctionName=function)
    say('%s unpublished' % (function))


@click.command(help='Schedule a function to run regularly.')
@click.option('--function', help="Defaults to the function in the current dir.")
@click.option('--rate', required=True,
              help='Execution rate. Like "6 minutes", or "1 day".')
def schedule(function, rate):
    if not function:
        function = metadata.read()['function']
    events = boto3.client('events')

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
        ScheduleExpression='rate(%s)' % rate,
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
    @click.group()
    def cli():
        pass

    subcommands = [create, list_published, build, publish, run, schedule,
                   unpublish]
    for cmd in subcommands:
        cli.add_command(cmd)
    cli()


if __name__ == '__main__':
    main()
