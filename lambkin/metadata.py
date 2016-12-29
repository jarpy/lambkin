import json
import os

metadata_file = 'metadata.json'
defaults = {
    'timeout': 60,
    'memory': 128,
    'role': 'lambda_basic_execution'
}


def get(key):
    """Return a single named property from the metadata.

    Defaults are returned for some properties if they are not stored in
    the metadata.json file.
    """
    try:
        return read()[key]
    except KeyError:
        return defaults[key]


def read():
    """Read metadata for a function from disk (metadata.json)."""
    if os.path.exists(metadata_file):
        with open(metadata_file) as f:
            return json.load(f)
    else:
        return {}


def write(subdirectory=None, **metadata):
    """Write keyword arguments, in JSON format, to metadata.json."""
    if subdirectory:
        path = os.path.join(subdirectory, metadata_file)
    else:
        path = metadata_file
    with open(path, 'w') as f:
        serialized = json.dumps(metadata, indent=4, sort_keys=True)
        f.write(serialized)


def update(**metadata):
    """Update the metadata file with any given values."""
    updated_metadata = read()
    for k, v in metadata.iteritems():
        updated_metadata[k] = metadata[k]
    write(**updated_metadata)
