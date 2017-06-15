#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

import os
import sys
sys.path.append("/home/vincent/Dropbox/Hacking/Active/devlpr") # @todo Remove (useful while developing devlpr)
sys.path.remove(os.getcwd())  # To avoid picking the development version of ActionTree inside devlpr


from devlpr import *

assert __name__ == "__main__"

devlpr = Devlpr()

devlpr.add_component(
    Python.Library(
        name="ActionTree",
        version="0.9.0",
        description="Executes (long) actions in parallel, respecting dependencies between those actions",
        home_page=GitHub.PAGES,
        license=MIT,
        py2="2.7",
        py3="3.5",
        status=BETA,
        classifier=[
            "Intended Audience :: Developers",
            "Topic :: Software Development",
        ],
        dependencies=dict(
            run=map(Python.Package, ["graphviz", "matplotlib", "wurlitzer"]),
            test=[Python.Package("mock", py2_only=True), System.Package("graphviz")],
        ),
    )
)

devlpr.main()
