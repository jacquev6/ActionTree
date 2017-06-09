==========
User guide
==========

Introduction
============

In ActionTree, you create the graph of the actions to be executed and then call the :func:`.execute` function on its root.

For example, let's say you want to generate three files, and then concatenate them into a fourth file.

First, import :mod:`.ActionTree`

>>> from ActionTree import Action, execute, DependencyGraph, GanttChart, CompoundException

Then create your specialized :class:`.Action` classes:

.. BEGIN_TEMPORARY_DOCTEST_IMPORT

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

.. END_TEMPORARY_DOCTEST_IMPORT

.. We have to import these classes to make them pickle-able in doctests


.. doctest::
    :hide:

    >>> import os
    >>> import pickle
    >>> pickle.loads(pickle.dumps(CreateFile("foo")))
    Traceback (most recent call last):
    ...
    PicklingError: Can't pickle <class 'CreateFile'>: it's not found as __builtin__.CreateFile

    >>> with open("doc/user_guide.rst") as in_f:
    ...   with open("temporary_doctest_import.py", "w") as out_f:
    ...     out_f.write("from ActionTree import Action\n\n")
    ...     do_output = False
    ...     for line in in_f:
    ...       if "END_TEMPORARY_DOCTEST_IMPORT" in line:
    ...         break
    ...       if do_output:
    ...         out_f.write(line[4:])
    ...       if "BEGIN_TEMPORARY_DOCTEST_IMPORT" in line:
    ...         do_output = True

    >>> from temporary_doctest_import import CreateFile, ConcatFiles
    >>> os.unlink("temporary_doctest_import.py")
    >>> import pickle
    >>> pickle.loads(pickle.dumps(CreateFile("foo")))
    <temporary_doctest_import.CreateFile object at 0x...>

Create an actions dependency graph:

>>> concat = ConcatFiles(["first", "second", "third"], "fourth")
>>> concat.add_dependency(CreateFile("first"))
>>> concat.add_dependency(CreateFile("second"))
>>> concat.add_dependency(CreateFile("third"))

And :func:`.execute` it:

>>> execute(concat)
<ActionTree.ExecutionReport object at 0x...>

You have no guaranty about the order of execution of the ``CreateFile`` actions,
but you are sure that they are all finished before the ``ConcatFiles`` action starts.

You can execute them in parallel, keeping the same guaranties:

>>> execute(concat, jobs=3).is_success
True

.. testcleanup::

    import os
    os.unlink("first")
    os.unlink("second")
    os.unlink("third")
    os.unlink("fourth")

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
>>> link_report = execute(link)

.. testcleanup::

    import os
    os.unlink("a.o")
    os.unlink("b.o")
    os.unlink("test")

.. @todo If you're really looking to compile stuff using ActionTree, you may want to have a look at devlpr

.. @todo Demonstrate return values and captured output

Drawings
========

You can draw a dependency graph with :class:`.DependencyGraph`:

>>> g = DependencyGraph(concat)
>>> g.write_to_png("doc/doctest/concat_dependency_graph.png")

.. figure:: doctest/concat_dependency_graph.png
    :align: center

    ``doc/doctest/concat_dependency_graph.png``

You can draw a Gantt chart of the execution with :class:`.GanttChart`:

>>> chart = GanttChart(link_report)
>>> chart.write_to_png("doc/doctest/link_gantt_chart.png")

.. figure:: doctest/link_gantt_chart.png
    :align: center

    ``doc/doctest/link_gantt_chart.png``

And if some action fails, you get:

>>> link.add_dependency(
...   CallSubprocess(["g++", "-c", "doc/c.cpp", "-o", "c.o"])
... )
>>> try:
...   execute(link, keep_going=True)
... except CompoundException as e:
...   chart = GanttChart(e.execution_report)
...   chart.write_to_png("doc/doctest/failed_link_gantt_chart.png")

.. figure:: doctest/failed_link_gantt_chart.png
    :align: center

    ``doc/doctest/failed_link_gantt_chart.png``
