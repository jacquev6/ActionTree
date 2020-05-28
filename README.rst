*ActionTree* is a Python (2.7 and 3.5+) library to execute (long) actions in parallel, respecting dependencies between those actions.
You create a dependency graph of actions to be executed and then call the ``execute`` function on its root.


It's licensed under the `MIT license <http://choosealicense.com/licenses/mit/>`_.
It's available on the `Python package index <http://pypi.python.org/pypi/ActionTree>`_.
Its `documentation <http://jacquev6.github.io/ActionTree>`_
and its `source code <https://github.com/jacquev6/ActionTree>`_ are on GitHub.

Questions? Remarks? Bugs? Want to contribute? `Open an issue <https://github.com/jacquev6/ActionTree/issues>`_!

Quick start
===========

Install from PyPI::

    $ pip install ActionTree

With dependencies to create Gantt charts and dependency graphs::

    $ pip install 'ActionTree[dependency_graphs,gantt]'

Import:

>>> from ActionTree import execute
>>> from ActionTree.stock import CallSubprocess

Execute some action:

>>> link = CallSubprocess(["g++", "a.o", "b.o", "-o", "test"])
>>> link.add_dependency(CallSubprocess(["g++", "-c", "a.cpp", "-o", "a.o"]))
>>> link.add_dependency(CallSubprocess(["g++", "-c", "b.cpp", "-o", "b.o"]))
>>> report = execute(link)

And verify everything went well:

>>> report.is_success
True
>>> os.path.isfile("test")
True
