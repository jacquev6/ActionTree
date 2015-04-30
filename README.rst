ActionTree is a Python (2.7+ and 3.3+) library to execute (long) actions in parallel, respecting dependencies between those actions.
You create the graph of the actions to be executed and then call the ``execute`` method of its root,
specifying how many actions must be run in parallel and if errors should stop the execution.

It's licensed under the `MIT license <http://choosealicense.com/licenses/mit/>`__.
It's available on the `Python package index <http://pypi.python.org/pypi/ActionTree>`__,
its `documentation is hosted by Python <http://pythonhosted.org/ActionTree>`__
and its source code is on `GitHub <https://github.com/jacquev6/ActionTree>`__.

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

.. image:: https://img.shields.io/github/issues/jacquev6/ActionTree.svg
    :target: https://github.com/jacquev6/ActionTree/issues

.. image:: https://badge.waffle.io/jacquev6/ActionTree.png?label=ready&title=ready
    :target: https://waffle.io/jacquev6/ActionTree

.. image:: https://img.shields.io/github/forks/jacquev6/ActionTree.svg
    :target: https://github.com/jacquev6/ActionTree/network

.. image:: https://img.shields.io/github/stars/jacquev6/ActionTree.svg
    :target: https://github.com/jacquev6/ActionTree/stargazers

Quick start
===========

Install from PyPI::

    $ pip install ActionTree

.. Warning, these are NOT doctests because doctests aren't displayed on GitHub.

Import::

    >>> from ActionTree import *

Execute some action::

    @todoc