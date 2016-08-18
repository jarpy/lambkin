from click import echo


def say(message):
    """Write an info message to STDERR.

    We deliberatly send the message to STDERR to keep STDOUT clear for any
    JSON output we may return. Interleaving info messages would break the
    ability to pipe our output to a JSON parser.
    """
    echo(message, err=True)
