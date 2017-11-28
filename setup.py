from __future__ import absolute_import

from setuptools import setup
from lambkin.lambkin import VERSION

import os.path


if(os.path.isfile('README.md')):
    import pypandoc
    with open('README.rst', 'w') as rst:
	rst.write(pypandoc.convert('README.md', 'rst', format='md'))

setup(
    name='lambkin',
    packages=['lambkin'],
    version=VERSION,
    description='CLI tool for managing functions in AWS Lambda.',
    long_description=open('README.rst').read(),
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
