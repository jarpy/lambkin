from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = open('README.md').read()

setup(
    name='lambkin',
    packages=['lambkin'],
    version='0.1.9',
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
        'Development Status :: 3 - Alpha',
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
