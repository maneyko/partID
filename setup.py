#!/usr/bin/env python

"""
**partID** is a miniature library to get the *real dimensions* of an
object from an image with a quarter. Various functions using OpenCV_
are used for the extraction of the part and quarter from the image, then
custom algorithms may be implemented to get certain features from the
part. In this case an algorithm to calculate thread pitch was developed.
For now the *height*, *width*, and *thread pitch* are measured to a mean
accuracy of 90% tested on over 40 different images.

.. _OpenCV: http://opencv.org/
"""

from setuptools import setup


with open('./requirements.txt') as f:
    contents = f.read().splitlines()
requirements = [line for line in contents if not line.startswith('#')]

setup(
    name='partID',
    author='Peter Maneykowski',
    version='0.2',
    license='MIT',
    url='https://github.com/maneyko/partID',
    description='Machine Part Image Identifier',
    long_description=__doc__,
    packages=['partID'],
    install_requires=requirements
)
