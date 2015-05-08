# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

"""
Introduction
============

In ActionTree, you create the graph of the actions to be executed and then call the ``execute`` method of its root.

For example, let's say you want to generate three files, and then concatenate them to a fourth file.

Let's start by the utility functions, not related to ActionTree:

>>> def create_file(name):
...   with open(name, "w") as f:
...     f.write("This is {}\\n".format(name))

>>> def concat_files(files, name):
...   with open(name, "w") as output:
...     for file in files:
...       with open(file) as input:
...         output.write(input.read())


Then, here is how you use them with ActionTree. Import it:

>>> from ActionTree import *

Create the graph of actions:

>>> from functools import partial

>>> concat = Action(partial(concat_files, ["first", "second", "third"], "fourth"), "concat")
>>> concat.add_dependency(Action(partial(create_file, "first"), "create first"))
>>> concat.add_dependency(Action(partial(create_file, "second"), "create second"))
>>> concat.add_dependency(Action(partial(create_file, "third"), "create third"))

Execute the actions:

>>> concat.execute()

You have no guaranty about the order of execution of the ``create_file`` actions,
but you are sure that they are all finished before the ``concat_files`` action starts.

You can execute them in parallel, keeping the same guaranties:

>>> concat.execute(jobs=3)

Stock actions
=============

ActionTree is shipped with some :mod:`~ActionTree.stock` actions for common tasks.

Say you want to compile two C++ files and link them:

>>> from ActionTree.stock import CallSubprocess

>>> link = CallSubprocess(["g++", "-o", "test", "a.o", "b.o"])
>>> link.add_dependency(CallSubprocess(["g++", "-c", "doc/a.cpp", "-o", "a.o"]))
>>> link.add_dependency(CallSubprocess(["g++", "-c", "doc/b.cpp", "-o", "b.o"]))
>>> link.execute(jobs=2)
"""

from .action import Action
from .exceptions import CompoundException
