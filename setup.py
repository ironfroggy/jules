#!/usr/bin/env python

from distutils.core import setup

INSTALL_REQUIRES = [
    'straight.plugin',
    'straight.command',
]

setup(name='jules',
    version='0.1-alpha-1',
    description='Yet Another Static Blog Generator I guess',
    author='Calvin Spealman',
    author_email='ironfroggy@gmail.com',
    packages=['jules'],
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
