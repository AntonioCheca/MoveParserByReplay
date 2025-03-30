#!/usr/bin/env python
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="move_parser_by_replay",
    version="0.0.1",
    author="Antonio Checa",
    description="Move Parser By Replay for SF6",
    license="GNU",
    keywords="",
    packages=['move_parser_by_replay', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Alpha",
    ],
)
