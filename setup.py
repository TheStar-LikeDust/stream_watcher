# -*- coding: utf-8 -*-
"""setup with setuptools."""

from setuptools import setup, find_packages

from stream_watcher import __version__

setup(
    name='stream_watcher',
    version=__version__,
    keywords='Stream',
    description='A Pythonic way to manage streams in one file.',
    author='Logic',
    author_email='logic.irl@outlook.com',
    url='https://github.com/DeliangFan/packagedemo',
    python_requires='>=3.8',
    packages=find_packages(exclude=['tests*']),
    license='Apache License 2.0'
)
