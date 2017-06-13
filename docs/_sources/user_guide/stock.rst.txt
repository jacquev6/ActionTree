Stock actions
=============

ActionTree is shipped with some :mod:`~.ActionTree.stock` actions for common tasks,
including running subprocesses and basic operations on files and directories.

Say you want to compile two C++ files and link them:

.. BEGIN SECTION stock_link.py

>>> from ActionTree import execute
>>> from ActionTree.stock import CreateDirectory, CallSubprocess

>>> make_build_dir = CreateDirectory("_build")

>>> compile_a = CallSubprocess(["g++", "-c", "a.cpp", "-o", "_build/a.o"])
>>> compile_a.add_dependency(make_build_dir)

>>> compile_b = CallSubprocess(["g++", "-c", "b.cpp", "-o", "_build/b.o"])
>>> compile_b.add_dependency(make_build_dir)

>>> link = CallSubprocess(["g++", "-o", "_build/test", "_build/a.o", "_build/b.o"])
>>> link.add_dependency(compile_a)
>>> link.add_dependency(compile_b)

.. END SECTION stock_link.py

>>> link_report = execute(link)

If you're really looking to compile stuff using :mod:`.ActionTree`,
you may want to have a look at `devlpr <https://github.com/jacquev6/devlpr>`__.
It's the reason why I wrote :mod:`.ActionTree` in the first place.
