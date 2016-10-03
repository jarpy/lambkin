from click import ClickException


def get_file_extension_for_runtime(runtime):
    """Return the correct file extension for a language runtime."""
    runtime = get_sane_runtime(runtime)
    if runtime.startswith('python'):
        return 'py'
    elif runtime.startswith('nodejs'):
        return 'js'


def get_language_name_for_runtime(runtime):
    if runtime.startswith('python'):
        return 'python'
    elif runtime.startswith('node'):
        return 'nodejs'


def get_sane_runtime(runtime):
    """Make a runtime string that Lambda will accept."""

    # Default to Python
    if runtime is None:
        runtime = 'python'

    # Ensure we specify a version, not just a language.
    if runtime == 'python':
        runtime = 'python2.7'
    if runtime == 'node' or runtime == 'nodejs':
        runtime = 'nodejs4.3'

    valid_runtimes = ['python2.7', 'nodejs4.3']
    if runtime in valid_runtimes:
        return runtime
    else:
        raise ClickException('Runtime "%s" is not supported' % runtime)
