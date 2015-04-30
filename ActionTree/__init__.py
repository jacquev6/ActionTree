# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

"""
@todoc doctests

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
"""

from .Action import Action
from .CompoundException import CompoundException
