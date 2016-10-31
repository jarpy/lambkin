import os
from click import ClickException
from subprocess import call, check_output
from os.path import join


def have_virtualenv():
    try:
        with open(os.devnull, 'w') as null:
            status = call(['virtualenv', '--help'], stdout=null, stderr=null)
        return status is 0
    except OSError:
        return False


def create_virtualenv(function_name):
    if not have_virtualenv():
        raise ClickException('Lambkin needs virtualenv. Please install it.')
    check_output([
        'virtualenv', '--python=python2.7', join(function_name, 'venv')
    ])


def run_in_virtualenv(command):
    """Run a shell command with the current function's virtualenv active."""
    return check_output('. venv/bin/activate && %s' % command, shell=True)
