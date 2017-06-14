*ActionTree* is a Python (2.7 and 3.5+) library to execute (long) actions in parallel, respecting dependencies between those actions.
You create a dependency graph of actions to be executed and then call the ``execute`` function on its root.

It's licensed under the `MIT license <http://choosealicense.com/licenses/mit/>`__.
It's available on the `Python package index <http://pypi.python.org/pypi/ActionTree>`__,
its `documentation <http://jacquev6.github.io/ActionTree>`__
and its `source code <https://github.com/jacquev6/ActionTree>`__ are on GitHub.

Questions? Remarks? Bugs? Want to contribute? `Open an issue <https://github.com/jacquev6/ActionTree/issues>`__!

.. image:: https://img.shields.io/travis/jacquev6/ActionTree/master.svg
    :target: https://travis-ci.org/jacquev6/ActionTree

.. image:: https://img.shields.io/coveralls/jacquev6/ActionTree/master.svg
    :target: https://coveralls.io/r/jacquev6/ActionTree

.. image:: https://img.shields.io/codeclimate/github/jacquev6/ActionTree.svg
    :target: https://codeclimate.com/github/jacquev6/ActionTree

.. image:: https://img.shields.io/scrutinizer/g/jacquev6/ActionTree.svg
    :target: https://scrutinizer-ci.com/g/jacquev6/ActionTree

.. image:: https://img.shields.io/pypi/dm/ActionTree.svg
    :target: https://pypi.python.org/pypi/ActionTree

.. image:: https://img.shields.io/pypi/l/ActionTree.svg
    :target: https://pypi.python.org/pypi/ActionTree

.. image:: https://img.shields.io/pypi/v/ActionTree.svg
    :target: https://pypi.python.org/pypi/ActionTree

.. image:: https://img.shields.io/pypi/pyversions/ActionTree.svg
    :target: https://pypi.python.org/pypi/ActionTree

.. image:: https://img.shields.io/pypi/status/ActionTree.svg
    :target: https://pypi.python.org/pypi/ActionTree

.. image:: https://img.shields.io/github/issues/jacquev6/ActionTree.svg
    :target: https://github.com/jacquev6/ActionTree/issues

.. image:: https://img.shields.io/github/forks/jacquev6/ActionTree.svg
    :target: https://github.com/jacquev6/ActionTree/network

.. image:: https://img.shields.io/github/stars/jacquev6/ActionTree.svg
    :target: https://github.com/jacquev6/ActionTree/stargazers

Quick start
===========

Install from PyPI::

    $ pip install ActionTree

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
