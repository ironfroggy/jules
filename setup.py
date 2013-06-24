#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()

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
