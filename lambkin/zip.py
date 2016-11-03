from __future__ import absolute_import

import os
import re
import zipfile
import lambkin.metadata as metadata

# REF: http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html


def create_zip():
    function = metadata.get('function')
    zip_file_path = '/tmp/lambkin-publish-%s.zip' % function
    zip_file = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk('.'):
        for f in files:
            path = os.path.join(root, f)
            regex = '\./venv/lib(?:64)?/python\d\.\d/(?:site|dist)-packages/(.*)'
            package_match = re.match(regex, path)
            if path.endswith('.pyc'):
                pass
            elif package_match:
                # Then strip the library dir, and put the file in the zip.
                trimmed_library_file = package_match.group(1)
                zip_file.write(path, trimmed_library_file)
            elif root.startswith('./venv') or root.startswith('./.git'):
                # Then it's other junk that we don't want.
                pass
            else:
                # Not sure what this is. The function author probably put
                # it here for a reason, so make sure it goes in the zip.
                zip_file.write(path, path)
    zip_file.close()
    return zip_file_path
