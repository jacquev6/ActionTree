Introduction
============

Actions and dependencies
------------------------

In :mod:`.ActionTree`, you create a dependency graph of actions to be executed and then call the :func:`.execute` function on its root.

For example, let's say you want to generate three files, and then concatenate them into a fourth file.

First, import :mod:`.ActionTree`

.. BEGIN SECTION introduction_actions.py

>>> from ActionTree import Action, execute

.. END SECTION introduction_actions.py

Then create your specialized :class:`.Action` classes:

.. BEGIN SECTION introduction_actions.py

>>> class CreateFile(Action):
...   def __init__(self, name):
...     super(CreateFile, self).__init__("create {}".format(name))
...     self.__name = name
...
...   def do_execute(self, dependency_statuses):
...     with open(self.__name, "w") as f:
...       f.write("This is {}\n".format(self.__name))

>>> class ConcatFiles(Action):
...   def __init__(self, files, name):
...     super(ConcatFiles, self).__init__("concat")
...     self.__files = files
...     self.__name = name
...
...   def do_execute(self, dependency_statuses):
...     with open(self.__name, "w") as output:
...       for file in self.__files:
...         with open(file) as input:
...           output.write(input.read())

.. END SECTION introduction_actions.py

.. We have to import these classes to make them picklable in doctests

.. doctest::
    :hide:

    >>> from introduction_actions import CreateFile, ConcatFiles

Create an actions dependency graph:

>>> concat = ConcatFiles(["first", "second", "third"], "fourth")
>>> concat.add_dependency(CreateFile("first"))
>>> concat.add_dependency(CreateFile("second"))
>>> concat.add_dependency(CreateFile("third"))

And :func:`.execute` it:

>>> execute(concat)
<ActionTree.ExecutionReport object at 0x...>

The actions have been executed successfully:

>>> def cat(name):
...   with open(name) as f:
...     print(f.read())

>>> cat("first")
This is first
<BLANKLINE>

>>> cat("second")
This is second
<BLANKLINE>

>>> cat("third")
This is third
<BLANKLINE>

>>> cat("fourth")
This is first
This is second
This is third
<BLANKLINE>

You have no guaranty about the order of execution of the ``CreateFile`` actions,
but you are sure that they are all finished before the ``ConcatFiles`` action starts.

You can execute them in parallel, keeping the same guaranties:

>>> execute(concat, jobs=3).is_success
True

Preview
-------

If you just want to know what *would* be done, you can use :meth:`.Action.get_possible_execution_order`:

>>> [a.label for a in concat.get_possible_execution_order()]
['create first', 'create second', 'create third', 'concat']

As said earlier, you have no guaranty about the order of the first three actions,
so :meth:`~.Action.get_possible_execution_order` returns *one* possible order.
