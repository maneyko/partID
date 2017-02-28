#!/usr/bin/env python

"""
*partID* is a miniature library to process images containing a quarter
and a machine part. Once the part is located, various dimensions may be
calculated.  For now only the height, width, and thread pitch are
measured.
"""

from setuptools import setup

setup(
    name='partID',
    author='Peter Maneykowski',
    version='0.2',
    license='MIT',
    url='https://github.com/maneyko/partID',
    description='Machine Part Image Identifier',
    long_description=__doc__,
    packages=['partID'],
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'six'
    ]
)
