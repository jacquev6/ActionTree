Outputs and side-effects
========================

Return values, exceptions and printed output
--------------------------------------------

Return values, exceptions and printed output are captured and returned by :func:`.execute` in the :class:`.ExecutionReport`.

.. @todo Demonstrate return values and captured output

.. @todo Demonstrate timing information (and link to demo of Gantt chart)

Other side effects
------------------

:mod:`.ActionTree` makes no attempt to handle any other side effect.

Each action is executed in its own process, so it should be safe to modify process-wide data
like the current working directory or environment variables.
