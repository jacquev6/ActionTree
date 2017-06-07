==========
User guide
==========

Introduction
============

In ActionTree, you create the graph of the actions to be executed and then call the ``execute`` method of its root.

For example, let's say you want to generate three files, and then concatenate them into a fourth file.

First, import ActionTree

>>> from ActionTree import *

Then create your specialized action classes:

>>> class CreateFile(Action):
...   def __init__(self, name):
...     super(CreateFile, self).__init__("create {}".format(name))
...     self.__name = name
...
...   def do_execute(self):
...     with open(self.__name, "w") as f:
...       f.write("This is {}\\n".format(self.__name))

>>> class ConcatFiles(Action):
...   def __init__(self, files, name):
...     super(ConcatFiles, self).__init__("concat")
...     self.__files = files
...     self.__name = name
...
...   def do_execute(self):
...     with open(self.__name, "w") as output:
...       for file in self.__files:
...         with open(file) as input:
...           output.write(input.read())

Create an actions dependency graph:

>>> concat = ConcatFiles(["first", "second", "third"], "fourth")
>>> concat.add_dependency(CreateFile("first"))
>>> concat.add_dependency(CreateFile("second"))
>>> concat.add_dependency(CreateFile("third"))

And execute it:

>>> concat.execute()

You have no guaranty about the order of execution of the ``CreateFile`` actions,
but you are sure that they are all finished before the ``ConcatFiles`` action starts.

You can execute them in parallel, keeping the same guaranties:

>>> concat.execute(jobs=3)

.. testcleanup::

    import os
    os.unlink("first")
    os.unlink("second")
    os.unlink("third")
    os.unlink("fourth")

Simple actions from callable
============================

:class:`.ActionFromCallable` accepts a callable in its constructor to be usable without subclassing.
The previous example could be rewriten like:

>>> def create_file(name):
...   with open(name, "w") as f:
...     f.write("This is {}\\n".format(name))

>>> def concat_files(files, name):
...   with open(name, "w") as output:
...     for file in files:
...       with open(file) as input:
...         output.write(input.read())

>>> concat = ActionFromCallable(lambda: concat_files(["first", "second", "third"], "fourth"), "concat")
>>> concat.add_dependency(ActionFromCallable(lambda: create_file("first"), "create first"))
>>> concat.add_dependency(ActionFromCallable(lambda: create_file("second"), "create second"))
>>> concat.add_dependency(ActionFromCallable(lambda: create_file("third"), "create third"))

>>> concat.execute()

Preview
=======

If you just want to know what *would* be done, use :meth:`.Action.get_preview`:

>>> concat.get_preview()
['create ...', 'create ...', 'create ...', 'concat']

As said earlier, you have no guaranty about the order of the first three actions,
so :meth:`~.Action.get_preview` returns one possible order.

The values returned by :meth:`~.Action.get_preview` are the labels passed in the constructor of :class:`.Action`,
so they can be anything you want, not just strings.

Stock actions
=============

ActionTree is shipped with some :mod:`~ActionTree.stock` actions for common tasks.

Say you want to compile two C++ files and link them:

>>> from ActionTree.stock import CallSubprocess

>>> link = CallSubprocess(["g++", "-o", "test", "a.o", "b.o"])
>>> link.add_dependency(
...   CallSubprocess(["g++", "-c", "doc/a.cpp", "-o", "a.o"])
... )
>>> link.add_dependency(
...   CallSubprocess(["g++", "-c", "doc/b.cpp", "-o", "b.o"])
... )
>>> link.execute(jobs=2)

.. testcleanup::

    os.unlink("a.o")
    os.unlink("b.o")
    os.unlink("test")

Drawings
========

You can easily draw a graph of your action and its dependencies with :class:`.DependencyGraph`:

>>> from ActionTree.drawings import DependencyGraph
>>> g = DependencyGraph(concat)
>>> g.write_to_png("doc/doctest/concat.png")

.. figure:: doctest/concat.png
    :align: center

    ``doc/doctest/concat.png``

You can draw an execution report with :class:`.ExecutionReport`:

>>> from ActionTree.drawings import ExecutionReport
>>> report = ExecutionReport(link)
>>> report.write_to_png("doc/doctest/link_report.png")

.. figure:: doctest/link_report.png
    :align: center

    ``doc/doctest/link_report.png``

And if some action fails, you get:

>>> link.add_dependency(
...   CallSubprocess(["g++", "-c", "doc/c.cpp", "-o", "c.o"])
... )
>>> link.execute(keep_going=True)
Traceback (most recent call last):
  ...
CompoundException: [CalledProcessError()]
>>> ExecutionReport(link).write_to_png("doc/doctest/failed_link_report.png")

.. figure:: doctest/failed_link_report.png
    :align: center

    ``doc/doctest/failed_link_report.png``
