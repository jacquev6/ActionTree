.. _outputs:

Outputs and side-effects
========================

Return values, exceptions and printed output
--------------------------------------------

Return values, exceptions and printed output are captured and returned by :func:`.execute` in the :class:`.ExecutionReport`.

.. @todoc Demonstrate return values and captured output
.. @todoc Add a note about keep_going
.. @todoc Add a note about the execution report in the CompoundException

Other side effects
------------------

`ActionTree` makes no attempt to handle any other side effect.

Each action is executed in its own process, so it should be safe to modify process-wide data
like the current working directory or environment variables.

.. @todoc Add a note about printing anything in do_execute
.. @todoc Add a note saying that outputs, return values and exceptions are captured
.. @todoc Add a note saying that output channels MUST be flushed before returning
.. @todoc Add a note saying that the class, the return value and any exceptions raised MUST be picklable
