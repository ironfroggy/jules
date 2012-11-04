#!/usr/bin/env python

from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'straight.plugin',
    'straight.command',
    'pyyaml',
    'jinja2',
    'docutils',
]

setup(name='jules',
    version='0.2.0.1',
    description='Yet Another Static Blog Generator I guess',
    author='Calvin Spealman',
    author_email='ironfroggy@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Environment :: Plugins',
    ],
    scripts = [
        'bin/jules',
    ]
)
