.. _outputs:

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

.. @todo Add a note about printing anything in do_execute
.. @todo Add a note saying that outputs, return values and exceptions are captured
.. @todo Add a note saying that output channels MUST be flushed before returning
.. @todo Add a note saying that the class, the return value and any exceptions raised MUST be picklable
