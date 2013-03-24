ActionTree executes (long) actions in parallel, respecting dependencies between those actions.

You create the graph of the actions to be executed and then call the ``execute`` method of its root,
specifying how many actions must be run in parallel and if errors should stop the execution.

Documentation
=============

See http://jacquev6.github.com/ActionTree
