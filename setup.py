#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

import setuptools
import textwrap

version = "0.3.0"


if __name__ == "__main__":
    setuptools.setup(
        name="ActionTree",
        version=version,
        description="Executes (long) actions in parallel, respecting dependencies between those actions",
        author="Vincent Jacques",
        author_email="vincent@vincent-jacques.net",
        url="http://jacquev6.github.com/ActionTree",
        long_description=textwrap.dedent("""\
        ActionTree executes (long) actions in parallel, respecting dependencies between those actions.

        You create the graph of the actions to be executed and then call the ``execute`` method of its root,
        specifying how many actions must be run in parallel and if errors should stop the execution.

        Documentation
        =============

        See http://jacquev6.github.com/ActionTree
        """),
        packages=[
            "ActionTree",
            "ActionTree.tests",
        ],
        package_data={
            "ActionTree": ["COPYING*"],
        },
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "Topic :: Software Development",
        ],
        test_suite="ActionTree.tests.AllTests",
        use_2to3=True
    )
