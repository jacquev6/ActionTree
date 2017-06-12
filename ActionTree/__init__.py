# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import concurrent.futures as futures
import contextlib
import datetime
import io
import multiprocessing
import os.path
import pickle
import Queue
import sys

import graphviz
import matplotlib
import matplotlib.dates
import matplotlib.figure
import matplotlib.backends.backend_agg
import wurlitzer


# @todo Make this queue Execution-specific
outputs_queue = multiprocessing.Queue()


class Hooks(object):
    def action_pending(self, action):
        pass

    def action_ready(self, action):
        pass

    # def action_started(self, action):
    #     pass

    def action_printed(self, action, text):
        pass

    def action_successful(self, action):
        pass

    def action_failed(self, action):
        pass

    def action_canceled(self, action):
        pass


def execute(action, jobs=1, keep_going=False, do_raise=True, hooks=Hooks()):
    """
    Recursively execute an action's dependencies then the action.

    :param Action action: the action to execute.
    :param int jobs: number of actions to execute in parallel. Pass ``None`` to let ActionTree choose.
    :param bool keep_going: if ``True``, then execution does not stop on first failure,
        but executes as many dependencies as possible.
    :param bool do_raise: if ``False``, then exceptions are caught and put in the :class:`.ExecutionReport`.
    :param hooks: @todo Document

    :raises CompoundException: when ``do_raise`` is ``True`` and dependencies raise exceptions.

    :rtype: ExecutionReport
    """
    return Executor(jobs, keep_going, do_raise).execute(action, hooks)


class ExecutionReport(object):
    """
    ExecutionReport()

    Execution report, returned by :func:`.execute`.
    """

    class ActionStatus(object):
        """
        ActionStatus()

        Status of a single :class:`.Action`.
        """

        Successful = "Successful"
        "The :attr:`status` after a successful execution."
        Canceled = "Canceled"
        "The :attr:`status` after a failed execution where a dependency raised an exception."
        Failed = "Failed"
        "The :attr:`status` after a failed execution where this action raised an exception."

        def __init__(
            self,
            ready_time=None, start_time=None, cancel_time=None, failure_time=None, success_time=None,
            return_value=None, exception=None, output=None
        ):
            if start_time:
                assert ready_time
                assert not cancel_time
                assert (failure_time or success_time)
                assert output is not None
                # return_value can be whatever was returned, including None
                if success_time:
                    assert not exception
                    self.__status = self.Successful
                else:
                    assert exception
                    self.__status = self.Failed
            else:
                # ready_time can be None if the action was canceled before it was ever ready,
                # or not None if it was ready, then canceled
                assert cancel_time
                assert not (failure_time or success_time)
                assert not output
                assert return_value is None
                self.__status = self.Canceled
            self.__ready_time = ready_time
            self.__cancel_time = cancel_time
            self.__start_time = start_time
            self.__failure_time = failure_time
            self.__success_time = success_time
            self.__return_value = return_value
            self.__exception = exception
            self.__output = output

        @property
        def status(self):
            """
            @todo Document
            """
            return self.__status

        @property
        def ready_time(self):
            """
            The local :class:`~datetime.datetime` when this action was ready to execute.
            """
            return self.__ready_time

        @property
        def start_time(self):
            """
            The local :class:`~datetime.datetime` at the begining of the execution of this action.
            """
            return self.__start_time

        @property
        def success_time(self):
            """
            The local :class:`~datetime.datetime` at the successful end of the execution of this action.
            """
            return self.__success_time

        @property
        def failure_time(self):
            """
            The local :class:`~datetime.datetime` at the successful end of the execution of this action.
            """
            return self.__failure_time

        @property
        def cancel_time(self):
            """
            The local :class:`~datetime.datetime` when this action was canceled.
            """
            return self.__cancel_time

        @property
        def return_value(self):
            """
            @todo Document
            """
            return self.__return_value

        @property
        def exception(self):
            """
            @todo Document
            """
            return self.__exception

        @property
        def output(self):
            """
            @todo Document
            """
            return self.__output

    def __init__(self):
        self.__is_success = True
        self.__action_statuses = dict()

    def set_success(self, is_success):
        self.__is_success = is_success

    @property
    def is_success(self):
        """
        ``True`` if the execution finished without error.

        :rtype: bool
        """
        return self.__is_success

    def set_action_status(self, action, status):
        self.__action_statuses[action] = status

    def get_action_status(self, action):
        """
        @todo Document
        """
        return self.__action_statuses[action]

    def get_actions_and_statuses(self):
        """
        @todo Document
        """
        return self.__action_statuses.items()


@contextlib.contextmanager
def redirect(action_id):  # pragma no cover (Executed in child process)
    # This is a highly contrieved use of Wurlitzer:
    # We just need to *capture* standards streams, so we trick Wurlitzer,
    # passing True instead of writeable file-like objects, and we redefine
    # _handle_xxx methods to intercept what it would write
    w = wurlitzer.Wurlitzer(stdout=True, stderr=True)

    def handle(data):
        outputs_queue.put((action_id, data))

    w._handle_stdout = handle
    w._handle_stderr = handle
    with w:
        yield


def _time_execute(action_id, action):  # pragma no cover (Executed in child process)
    exception = None
    return_value = None
    start_time = datetime.datetime.now()
    try:
        with redirect(action_id):
            return_value = action.do_execute()
    except Exception as e:
        exception = e
    end_time = datetime.datetime.now()
    ret = (exception, return_value, start_time, end_time)
    _check_picklability(ret)
    outputs_queue.put((action_id, None))
    return ret


def _check_picklability(stuff):
    # This is a way to fail fast if we see a non-picklable object
    # because ProcessPoolExecutor freezes forever if we try to transfer
    # a non-picklable object through its queues
    pickle.loads(pickle.dumps(stuff))


class Executor(object):
    def __init__(self, jobs, keep_going, do_raise):
        self.__jobs = jobs
        self.__keep_going = keep_going
        self.__do_raise = do_raise

    class Execution:
        # An aggregate for things that cannot be stored in Executor
        # (to allow several parallel calls to Executor.execute)
        def __init__(self, executor, pending, hooks):
            self.hooks = hooks
            self.executor = executor
            self.pending = set(pending)  # Action
            self.actions_by_id = {id(action): action for action in pending}  # id -> Action
            self.submitted = set()  # Future
            self.ready_times = dict()  # Action -> datetime.datetime
            self.outputs = dict()  # Action -> list of str (with object() and None sentinels at begin and end)
            self.succeeded = set()  # Action
            self.failed = set()  # Action
            self.exceptions = []
            self.report = ExecutionReport()

    def execute(self, action, hooks):
        # To avoid races, threads in pools only call pure functions (with no side effects),
        # and only the thread calling Executor.execute is allowed to modify anything.

        # assert outputs_queue.empty()

        with futures.ProcessPoolExecutor(max_workers=self.__jobs) as executor:
            execution = Executor.Execution(executor, action.get_all_dependencies(), hooks)
            _check_picklability(execution.pending)
            for action in execution.pending:
                execution.hooks.action_pending(action)
            while execution.pending or execution.submitted:
                self.__progress(execution)

        # assert outputs_queue.empty()

        if self.__do_raise and execution.exceptions:
            raise CompoundException(execution.exceptions, execution.report)
        else:
            return execution.report

    def __progress(self, execution):
        now = datetime.datetime.now()
        if self.__keep_going or not execution.exceptions:
            self.__submit_or_cancel(execution, now)
        else:
            self.__cancel(execution, now)
        self.__wait(execution)

    def __submit_or_cancel(self, execution, now):
        go_on = True
        while go_on:
            go_on = False
            for action in set(execution.pending):
                done = execution.succeeded | execution.failed
                if all(d in done for d in action.dependencies):
                    if any(d in execution.failed for d in action.dependencies):
                        self.__mark_action_canceled(execution, action, cancel_time=now)
                        execution.pending.remove(action)
                        go_on = True
                    else:
                        self.__submit_action(execution, action, ready_time=now)
                        go_on = True

    def __cancel(self, execution, now):
        for future in list(execution.submitted):
            if future.cancel():
                self.__mark_action_canceled(execution, future.action, cancel_time=now)
                execution.submitted.remove(future)
        for action in execution.pending:
            self.__mark_action_canceled(execution, action, cancel_time=now)
        execution.pending.clear()

    def __dequeue_some_output(self, execution):
        try:
            (action_id, output) = outputs_queue.get_nowait()
            action = execution.actions_by_id[action_id]
            execution.outputs[action].append(output)
            if output is not None:
                execution.hooks.action_printed(action, output)
        except Queue.Empty:
            pass

    def __wait(self, execution):
        self.__dequeue_some_output(execution)
        waited = futures.wait(execution.submitted, return_when=futures.FIRST_COMPLETED, timeout=0.1)
        for future in waited.done:
            execution.submitted.remove(future)
            (exception, return_value, start_time, end_time) = future.result()
            ready_time = execution.ready_times[future.action]
            while execution.outputs[future.action][-1] is not None:
                self.__dequeue_some_output(execution)
            output = b"".join(execution.outputs[future.action][1:-1])
            if exception:
                self.__acknowledge_action_failure(
                    execution, future.action,
                    ready_time=ready_time, start_time=start_time, failure_time=end_time,
                    exception=exception, output=output,
                )
            else:
                self.__acknowledge_action_success(
                    execution, future.action,
                    ready_time=ready_time, start_time=start_time, success_time=end_time,
                    return_value=return_value, output=output,
                )

    @classmethod
    def __submit_action(cls, execution, action, ready_time):
        future = execution.executor.submit(_time_execute, id(action), action)
        future.action = action
        execution.submitted.add(future)
        execution.outputs[action] = [object()]
        execution.ready_times[action] = ready_time
        execution.pending.remove(action)
        execution.hooks.action_ready(action)

    @staticmethod
    def __mark_action_canceled(execution, action, cancel_time):
        execution.failed.add(action)
        execution.report.set_action_status(
            action,
            ExecutionReport.ActionStatus(
                ready_time=execution.ready_times.get(action),
                cancel_time=cancel_time,
            )
        )
        execution.hooks.action_canceled(action)

    @staticmethod
    def __acknowledge_action_success(execution, action, ready_time, start_time, success_time, return_value, output):
        execution.succeeded.add(action)
        execution.report.set_action_status(
            action,
            ExecutionReport.ActionStatus(
                ready_time=ready_time,
                start_time=start_time,
                success_time=success_time,
                return_value=return_value,
                output=output,
            ),
        )
        execution.hooks.action_successful(action)

    @staticmethod
    def __acknowledge_action_failure(execution, action, ready_time, start_time, failure_time, exception, output):
        execution.exceptions.append(exception)
        execution.report.set_success(False)
        execution.failed.add(action)
        execution.report.set_action_status(
            action,
            ExecutionReport.ActionStatus(
                ready_time=ready_time,
                start_time=start_time,
                failure_time=failure_time,
                exception=exception,
                output=output,
            )
        )
        execution.hooks.action_failed(action)


class Action(object):
    """
    The main class of ActionTree.
    An action to be started after all its dependencies are finished.
    Pass it to :func:`.execute`.

    This is a base class for your custom actions.
    You must define a ``def do_execute(self):`` method that performs the action.
    Its return value is ignored.
    If it raises and exception, it is captured and re-raised in a :exc:`CompoundException`.

    """
    # @todo Add a note about printing anything in do_execute
    # @todo Add a note saying that outputs, return values and exceptions are captured
    # @todo Add a note saying that output channels MUST be flushed before returning
    # @todo Add a note saying that the class, the return value and any exceptions raised MUST be picklable

    def __init__(self, label):
        """
        :param label: whatever you want to attach to the action.
            Can be retrieved by :attr:`label` and :meth:`get_preview`.
        """
        self.__label = label
        self.__dependencies = set()

    @property
    def label(self):
        """
        The label passed to the constructor.
        """
        return self.__label

    def add_dependency(self, dependency):
        """
        Add a dependency to be executed before this action.
        Order of insertion of dependencies is not important.

        :param Action dependency:

        :raises DependencyCycleException: when adding the new dependency would create a cycle.
        """
        if self in dependency.get_all_dependencies():
            raise DependencyCycleException()
        self.__dependencies.add(dependency)

    @property
    def dependencies(self):
        """
        Return the list of this action's dependencies.
        """
        return list(self.__dependencies)

    def get_all_dependencies(self):
        """
        Return the set of this action's recursive dependencies, including itself.
        """
        dependencies = set([self])
        for dependency in self.__dependencies:
            dependencies |= dependency.get_all_dependencies()
        return dependencies

    def get_preview(self):
        """
        Return the labels of this action and its dependencies, in an order that could be the execution order.
        """
        return [action.__label for action in self.get_possible_execution_order()]

    def get_possible_execution_order(self, seen_actions=None):
        if seen_actions is None:
            seen_actions = set()
        actions = []
        if self not in seen_actions:
            seen_actions.add(self)
            for dependency in self.__dependencies:
                actions += dependency.get_possible_execution_order(seen_actions)
            actions.append(self)
        return actions


class CompoundException(Exception):
    """
    Exception thrown by :func:`.execute` when a dependencies raise exceptions.
    """

    def __init__(self, exceptions, execution_report):
        super(CompoundException, self).__init__(exceptions)
        self.__exceptions = exceptions
        self.__execution_report = execution_report

    @property
    def exceptions(self):
        """
        The list of the encapsulated exceptions.
        """
        return self.__exceptions

    @property
    def execution_report(self):
        """
        The :class:`.ExecutionReport` of the failed execution.
        """
        return self.__execution_report


class DependencyCycleException(Exception):
    """
    Exception thrown by :meth:`.Action.add_dependency` when adding the new dependency would create a cycle.
    """

    def __init__(self):
        super(DependencyCycleException, self).__init__("Dependency cycle")


class DependencyGraph(object):
    """
    @todo Document
    """

    def __init__(self, action):
        self.__graphviz_graph = graphviz.Digraph("action", node_attr={"shape": "box"})
        nodes = {}
        for (i, action) in enumerate(action.get_possible_execution_order()):
            node = str(i)
            nodes[action] = node
            self.__graphviz_graph.node(node, str(action.label))
            for dependency in action.dependencies:
                assert dependency in nodes  # Because we are iterating a possible execution order
                self.__graphviz_graph.edge(node, nodes[dependency])

    def write_to_png(self, filename):  # pragma no cover (Untestable? But small.)
        """
        Write the graph as a PNG image to the specified file.

        See also :meth:`get_graphviz_graph` if you want to draw the graph somewhere else.
        """
        directory = os.path.dirname(filename)
        filename = os.path.basename(filename)
        filename, ext = os.path.splitext(filename)
        g = self.get_graphviz_graph()
        g.format = "png"
        g.render(directory=directory, filename=filename, cleanup=True)

    def get_graphviz_graph(self):
        """
        Return a :class:`graphviz.Digraph` of this dependency graph.

        See also :meth:`write_to_png` for the simplest use-case.
        """
        return self.__graphviz_graph.copy()


class GanttChart(object):  # pragma no cover (Too difficult to unit test)
    """
    @todo Document
    """

    def __init__(self, report):
        # @todo Sort actions somehow to improve readability (top-left to bottom-right)
        self.__actions = {
            id(action): self.__make_action(action, status)
            for (action, status) in report.get_actions_and_statuses()
        }

    # @todo Factorize Actions
    class SuccessfulAction(object):
        def __init__(self, action, status):
            self.__label = str(action.label)
            self.__id = id(action)
            self.__dependencies = set(id(d) for d in action.dependencies)
            self.__ready_time = status.ready_time
            self.__start_time = status.start_time
            self.__success_time = status.success_time

        @property
        def min_time(self):
            return self.__ready_time

        @property
        def max_time(self):
            return self.__success_time

        def draw(self, ax, ordinates, actions):
            ordinate = ordinates[self.__id]
            ax.plot([self.__ready_time, self.__start_time], [ordinate, ordinate], color="blue", lw=1)
            # @todo Use an other end-style to avoid pixels before/after min/max_time
            ax.plot([self.__start_time, self.__success_time], [ordinate, ordinate], color="blue", lw=4)
            # @todo Make sure the text is not outside the plot on the right
            ax.annotate(self.__label, xy=(self.__start_time, ordinate), xytext=(0, 3), textcoords="offset points")
            for d in self.__dependencies:
                ax.plot([actions[d].max_time, self.min_time], [ordinates[d], ordinate], "k:", lw=1)

    class FailedAction(object):
        def __init__(self, action, status):
            self.__label = str(action.label)
            self.__id = id(action)
            self.__dependencies = set(id(d) for d in action.dependencies)
            self.__ready_time = status.ready_time
            self.__start_time = status.start_time
            self.__failure_time = status.failure_time

        @property
        def min_time(self):
            return self.__ready_time

        @property
        def max_time(self):
            return self.__failure_time

        def draw(self, ax, ordinates, actions):
            ordinate = ordinates[self.__id]
            ax.plot([self.__ready_time, self.__start_time], [ordinate, ordinate], color="red", lw=1)
            ax.plot([self.__start_time, self.__failure_time], [ordinate, ordinate], color="red", lw=4)
            ax.annotate(self.__label, xy=(self.__start_time, ordinate), xytext=(0, 3), textcoords="offset points")
            for d in self.__dependencies:
                ax.plot([actions[d].max_time, self.min_time], [ordinates[d], ordinate], "k:", lw=1)

    class CanceledAction(object):
        def __init__(self, action, status):
            self.__label = str(action.label)
            self.__id = id(action)
            self.__dependencies = set(id(d) for d in action.dependencies)
            self.__ready_time = status.ready_time
            self.__cancel_time = status.cancel_time

        @property
        def min_time(self):
            return self.__cancel_time if self.__ready_time is None else self.__ready_time

        @property
        def max_time(self):
            return self.__cancel_time

        def draw(self, ax, ordinates, actions):
            ordinate = ordinates[self.__id]
            if self.__ready_time:
                ax.plot([self.__ready_time, self.__cancel_time], [ordinate, ordinate], color="grey", lw=1)
            ax.annotate(
                "(Canceled) {}".format(self.__label),
                xy=(self.__cancel_time, ordinate),
                xytext=(0, 3),
                textcoords="offset points"
            )
            for d in self.__dependencies:
                ax.plot([actions[d].max_time, self.min_time], [ordinates[d], ordinate], "k:", lw=1)

    @classmethod
    def __make_action(cls, action, status):
        if status.status == ExecutionReport.ActionStatus.Successful:
            return cls.SuccessfulAction(action, status)
        elif status.status == ExecutionReport.ActionStatus.Failed:
            return cls.FailedAction(action, status)
        elif status.status == ExecutionReport.ActionStatus.Canceled:
            return cls.CanceledAction(action, status)

    def write_to_png(self, filename):
        """
        Write the Gantt chart as a PNG image to the specified file.

        See also :meth:`get_mpl_figure` and :meth:`plot_on_mpl_axes` if you want to draw the report somewhere else.
        """
        figure = self.get_mpl_figure()
        canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(figure)
        canvas.print_figure(filename)

    def get_mpl_figure(self):
        """
        Return a :class:`matplotlib.figure.Figure` of this Gantt chart.

        See also :meth:`plot_on_mpl_axes` if you want to draw the Gantt chart on your own matplotlib figure.

        See also :meth:`write_to_png` for the simplest use-case.
        """
        fig = matplotlib.figure.Figure()
        ax = fig.add_subplot(1, 1, 1)

        self.plot_on_mpl_axes(ax)

        return fig

    @staticmethod
    def __nearest(v, values):
        for i, value in enumerate(values):
            if v < value:
                break
        if i == 0:
            return values[0]
        else:
            if v - values[i - 1] <= values[i] - v:
                return values[i - 1]
            else:
                return values[i]

    __intervals = [
        1, 2, 5, 10, 15, 30, 60,
        2 * 60, 10 * 60, 30 * 60, 3600,
        2 * 3600, 3 * 3600, 6 * 3600, 12 * 3600, 24 * 3600,
    ]

    def plot_on_mpl_axes(self, ax):
        """
        Plot this Gantt chart on the provided :class:`matplotlib.axes.Axes`.

        See also :meth:`write_to_png` and :meth:`get_mpl_figure` for the simpler use-cases.
        """
        ordinates = {ident: len(self.__actions) - i for (i, ident) in enumerate(self.__actions.iterkeys())}

        for action in self.__actions.itervalues():
            action.draw(ax, ordinates, self.__actions)

        ax.get_yaxis().set_ticklabels([])
        ax.set_ylim(0.5, len(self.__actions) + 1)

        min_time = min(a.min_time for a in self.__actions.itervalues()).replace(microsecond=0)
        max_time = (
            max(a.max_time for a in self.__actions.itervalues()).replace(microsecond=0) +
            datetime.timedelta(seconds=1)
        )
        duration = int((max_time - min_time).total_seconds())

        ax.set_xlabel("Local time")
        ax.set_xlim(min_time, max_time)
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
        ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(maxticks=4, minticks=5))

        ax2 = ax.twiny()
        ax2.set_xlabel("Relative time")
        ax2.set_xlim(min_time, max_time)
        ticks = range(0, duration, self.__nearest(duration // 5, self.__intervals))
        ax2.xaxis.set_ticks([min_time + datetime.timedelta(seconds=s) for s in ticks])
        ax2.xaxis.set_ticklabels(ticks)
