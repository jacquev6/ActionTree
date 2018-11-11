.. _resources:

Resources
=========

.. testsetup::

    import shutil

    from ActionTree import execute, GanttChart
    from ActionTree.stock import CallSubprocess

    from stock_link import *

    if os.path.exists("_build"):
      shutil.rmtree("_build")

More CPU cores
--------------

By default, *ActionTree* considers that all actions execute on a single core.
Thus, by default, the ``cpu_cores`` parameter of :func:`.execute` controls how many actions can be executed in parallel.

You can tell *ActionTree* that your :class:`.Action` uses more cores with :meth:`~.Action.require_resource` and :obj:`.CPU_CORE`:

(Here are the :ref:`source files <source_files>` used below.)

>>> from ActionTree import CPU_CORE

>>> compile_others = CallSubprocess(["make", "-j", "4", "_build/c.o", "_build/d.o", "_build/e.o", "_build/f.o", "_build/g.o", "_build/h.o"], label="make -j 4")
>>> compile_others.add_dependency(make_build_dir)
>>> compile_others.require_resource(CPU_CORE, 4)

>>> link_with_others = CallSubprocess(["g++", "-o", "_build/test", "_build/a.o", "_build/b.o", "_build/c.o", "_build/d.o", "_build/e.o", "_build/f.o", "_build/g.o", "_build/h.o"], label="g++ -o test")
>>> link_with_others.add_dependency(compile_a)
>>> link_with_others.add_dependency(compile_b)
>>> link_with_others.add_dependency(compile_others)

>>> GanttChart(execute(link_with_others, cpu_cores=4)).write_to_png("link_with_others_gantt_chart.png")

.. figure:: artifacts/link_with_others_gantt_chart.png
    :align: center

    ``link_with_others_gantt_chart.png``

As we expected, you can observe that the call to ``make`` was not executed at the same time as the individual calls to ``g++ -c``.

Arbitrary resources
-------------------

The same mechanism can be used with any instance of the :class:`.Resource` class.
If you want that no more than two actions of some kind execute at the same time,
while allowing other actions to run, just create a resource:

>>> from ActionTree import Resource
>>> from ActionTree.stock import Sleep, NullAction

>>> semaphore = Resource(2)
>>> dependencies = []
>>> for i in range(6):
...     d = Sleep(0.3, label="limited")
...     d.require_resource(semaphore)
...     dependencies.append(d)
>>> for i in range(5):
...     d = Sleep(0.4, label="free")
...     dependencies.append(d)
>>> with_resource = NullAction(dependencies=dependencies)

>>> GanttChart(execute(with_resource, cpu_cores=5)).write_to_png("with_resource_gantt_chart.png")

.. figure:: artifacts/with_resource_gantt_chart.png
    :align: center

    ``with_resource_gantt_chart.png``

As expected again, there was never more than two ``sleep 0.3`` actions running at the same time,
but ``sleep 0.4`` actions were free to execute.

:class:`.Resource`\ 's ``availability`` parameter and :meth:`~.Action.require_resource`\ 's ``quantity`` parameter
allow a flexible specification of which actions should not execute at the same time.
