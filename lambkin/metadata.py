import json
import os

metadata_file = 'metadata.json'


def read():
    """Read metadata for a function from disk (metadata.json)."""
    with open(metadata_file) as f:
        return json.load(f)


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
