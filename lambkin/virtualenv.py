from subprocess import check_output
from os.path import join


def create_virtualenv(function_name):
    check_output([
        'virtualenv', '--python=python2.7', join(function_name, 'venv')
    ])


def run_in_virtualenv(function_name, shell_command):
    return check_output('. %s/venv/bin/activate && %s' %
                 (function_name, shell_command), shell=True)
