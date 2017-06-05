#!/usr/bin/env python

from distutils.core import setup

setup(
    name='m',
    version='1.0.0',
    description='A high-level routing Web framework',
    author='flowsnow',
    author_email='snowlight437@gmail.com',
    license='MIT',
    packages=['m'],
    install_requires=[
        'WebOb>=1.6.1'
    ],
)
