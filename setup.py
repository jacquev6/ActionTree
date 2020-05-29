#!/usr/bin/env python
# coding: utf8

# Copyright 2012-2018 Vincent Jacques <vincent@vincent-jacques.net>
# Copyright 2017 Nelo-T. Wallus <nelo@wallus.de>

import setuptools
import sys

version = "0.13.2"


setuptools.setup(
    name="ActionTree",
    version=version,
    description="Executes (long) actions in parallel, respecting dependencies between those actions",
    long_description=open("README.rst").read(),
    author="Vincent Jacques",
    author_email="vincent@vincent-jacques.net",
    url="http://jacquev6.github.io/ActionTree",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
    ],
    packages=setuptools.find_packages(),
    extras_require={
        "dependency_graphs": open("requirements-dependency_graphs.txt").readlines(),
        "gantt": open("requirements-gantt.txt").readlines(),
    },
    test_suite="ActionTree.tests",
    command_options={
        "build_sphinx": {
            "version": ("setup.py", version),
            "release": ("setup.py", version),
            "source_dir": ("setup.py", "doc"),
        },
    },
)
