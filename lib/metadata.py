import json
from os.path import join

class Metadata():
    def __init__(self, function_name):
        self.function_name = function_name
        self.metadata_file = join('functions', function_name, 'metadata.json')

    def write(self, **metadata):
        """Write keyword arguments, in JSON format, to metadata.json."""
        with open(self.metadata_file, 'w') as f:
            serialized = json.dumps(metadata, indent=4, sort_keys=True)
            f.write(serialized)

    def read(self):
        """Read metadata for a function from disk (metadata.json)."""
        with open(self.metadata_file) as f:
            return json.load(f)
