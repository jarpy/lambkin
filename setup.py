from setuptools import setup

setup(
    name = 'lambkin',
    packages = ['lambkin'],
    version = '0.0.1',
    description = 'CLI tool for managing functions in AWS Lambda.',
    author='Toby McLaughlin',
    author_email='toby@jarpy.net',
    url='https://github.com/jarpy/lambkin',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
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
        'click>5,<7',
        'pystache'
    ]

)
