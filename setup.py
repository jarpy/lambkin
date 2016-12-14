from __future__ import absolute_import

from setuptools import setup
from lambkin.lambkin import VERSION

import pypandoc
long_description = pypandoc.convert('README.md', 'rst')

setup(
    name='lambkin',
    packages=['lambkin'],
    version=VERSION,
    description='CLI tool for managing functions in AWS Lambda.',
    long_description=long_description,
    author='Toby McLaughlin',
    author_email='toby@jarpy.net',
    url='https://github.com/jarpy/lambkin',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
    ],
    entry_points={
        'console_scripts': [
            'lambkin=lambkin.lambkin:main',
        ],
    },
    install_requires=[
        'boto3',
        'click>=6,<7',
        'pystache'
    ]

)
