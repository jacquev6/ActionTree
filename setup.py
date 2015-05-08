#!/usr/bin/env python
# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import setuptools

version = "0.5.0"


setuptools.setup(
    name="ActionTree",
    version=version,
    description="Executes (long) actions in parallel, respecting dependencies between those actions",
    author="Vincent Jacques",
    author_email="vincent@vincent-jacques.net",
    url="http://pythonhosted.org/ActionTree/",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development",
    ],
    install_requires=["AnotherPyGraphvizAgain"],
    tests_require=["MockMockMock"],
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
