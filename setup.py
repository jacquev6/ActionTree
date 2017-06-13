#!/usr/bin/env python
# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import setuptools
import sys


version = "0.8.0"


def py2_only(*dependencies):
    if sys.version_info[0] == 2:
        return list(dependencies)
    else:
        return []


setuptools.setup(
    name="ActionTree",
    version=version,
    description="Executes (long) actions in parallel, respecting dependencies between those actions",
    author="Vincent Jacques",
    author_email="vincent@vincent-jacques.net",
    url="http://jacquev6.github.io/ActionTree/",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development",
    ],
    install_requires=["graphviz", "matplotlib", "wurlitzer"],
    tests_require=py2_only("mock"),
    test_suite="ActionTree.tests",
    use_2to3=True,
    command_options={
        "build_sphinx": {
            "version": ("setup.py", version),
            "release": ("setup.py", version),
            "source_dir": ("setup.py", "doc"),
        },
    },
)
