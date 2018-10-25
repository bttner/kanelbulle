#!/usr/bin/env python3

"""setuptools installer script for kanelbulle."""

from setuptools import setup, find_packages

setup(
    name='kanelbulle',
    version='0.1.0',
    license='Apache-2.0',
    description='A server program to establish a socket communication.',
    author='Felix Büttner',

    packages=find_packages(),

    install_requires=['pytest', 'pytest-cov'],
    tests_require=['pytest', 'pytest-cov'],
)
