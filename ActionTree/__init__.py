# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of ActionTree. http://jacquev6.github.com/ActionTree

# ActionTree is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ActionTree is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with ActionTree.  If not, see <http://www.gnu.org/licenses/>.

"""
ActionTree
==========

Introduction
------------

ActionTree executes (long) actions in parallel, respecting dependencies between those actions.

You create the graph of the actions to be executed and then call the ``execute`` method of its root,
specifying how many actions must be run in parallel and if errors should stop the execution.

For example, let's say you want to generate three files, and then concatenate them to a fourth file.

Let's start by the utility functions, not related to ActionTree::

    def createFile(name):
        with open(name, "w") as f:
            f.write("This is " + name + "\\n")

    def concatFiles(files, name):
        with open(name, "w") as output:
            for file in files:
                with open(file) as input:
                    output.write(input.read())

Then, here is how you use them with ActionTree. Import it::

    from ActionTree import Action

Create the graph of actions::

    concat = Action(lambda: concatFiles(["first", "second", "third"], "fourth"), "concat")
    concat.addDependency(Action(lambda: createFile("first"), "create first"))
    concat.addDependency(Action(lambda: createFile("second"), "create second"))
    concat.addDependency(Action(lambda: createFile("third"), "create third"))

Execute the actions::

    concat.execute()

You have no guaranty about the order of execution of the ``createFile`` action, but you are sure that they
are all finished before the ``concatFiles`` action starts.

You can execute them in parallel, keeping the same guaranties::

    concat.execute(jobs=3)

Installation
------------

ActionTree is on `the Python Package Index <https://pypi.python.org/pypi/ActionTree>`_,
so ``easy_install ActionTree`` or ``pip install ActionTree`` should be enough.
You can also `clone it on Github <https://github.com/jacquev6/ActionTree>`_.

Licensing
---------

ActionTree is distributed under the GNU Lesser General Public Licence.
See files COPYING and COPYING.LESSER, as requested by `GNU <http://www.gnu.org/licenses/gpl-howto.html>`_.

Reference
---------

.. autoclass:: Action
    :members:

.. autoclass:: CompoundException()
    :members:
"""

from .Action import Action
from .CompoundException import CompoundException
