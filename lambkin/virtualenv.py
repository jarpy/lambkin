from subprocess import check_output
from os.path import join


def create_virtualenv(function_name):
    check_output([
        'virtualenv', '--python=python2.7', join(function_name, 'venv')
    ])


def run_in_virtualenv(command):
    """Run a shell command with the current function's virtualenv active."""
    return check_output('. venv/bin/activate && %s' % command, shell=True)
