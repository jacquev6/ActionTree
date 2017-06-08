# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import concurrent.futures as futures
import datetime
import multiprocessing
import os.path

import graphviz
import matplotlib
import matplotlib.dates
import matplotlib.figure
import matplotlib.backends.backend_agg


def execute(action, jobs=1, keep_going=False):
    """
    Recursively execute an action's dependencies then the action.

    :param Action action: the action to execute.
    :param int jobs: number of actions to execute in parallel. Pass ``None`` to let ActionTree choose.
    :param bool keep_going: if ``True``, then execution does not stop on first failure,
        but executes as many dependencies as possible.

    :raises CompoundException: when dependencies raise exceptions.

    :rtype: ExecutionReport
    """
    if jobs <= 0 or jobs is None:
        jobs = multiprocessing.cpu_count() + 1
    return Executor(jobs, keep_going).execute(action)


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

        def __init__(self, ready_time=None, start_time=None, cancel_time=None, failure_time=None, success_time=None):
            ready = bool(ready_time)
            start = bool(start_time)
            cancel = bool(cancel_time)
            failure = bool(failure_time)
            success = bool(success_time)
            if ready:
                if start:
                    assert not cancel
                    assert (failure or success)
                    self.__status = self.Successful if success else self.Failed
                else:
                    assert cancel
                    assert not (failure or success)
                    self.__status = self.Canceled
            else:
                assert cancel
                assert not (start or failure or success)
                self.__status = self.Canceled
            self.__ready_time = ready_time
            self.__cancel_time = cancel_time
            self.__start_time = start_time
            self.__success_time = success_time
            self.__failure_time = failure_time

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


class Executor(object):
    def __init__(self, jobs, keep_going):
        self.__jobs = jobs
        self.__keep_going = keep_going

    class Execution:
        # An aggregate for things that cannot be stored in Executor
        # (to allow several parallel calls to Executor.execute)
        def __init__(self, executor, pending):
            self.executor = executor
            self.pending = set(pending)  # Action
            self.submitted = dict()  # Future -> Action
            self.submitted_at = dict()  # Action -> datetime.datetime
            self.succeeded = set()  # Action
            self.failed = set()  # Action
            self.exceptions = []
            self.report = ExecutionReport()

    def execute(self, action):
        # Threads in pool just call self.__time_execute, which has no side effects.
        # To avoid races, only the thread calling Executor.execute is allowed to modify anything.

        with futures.ThreadPoolExecutor(max_workers=self.__jobs) as executor:
            execution = Executor.Execution(executor, action.get_all_dependencies())
            while execution.pending or execution.submitted:
                self.__progress(execution)

        if execution.exceptions:
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
                        self.__mark_action_canceled(execution, action, now)
                        execution.pending.remove(action)
                        go_on = True
                    else:
                        execution.submitted[execution.executor.submit(self.__time_execute, action)] = action
                        execution.submitted_at[action] = now
                        execution.pending.remove(action)
                        go_on = True

    @staticmethod
    def __time_execute(action):
        exception = None
        try:
            begin_time = datetime.datetime.now()
            action.do_execute()
        except Exception as e:
            exception = e
        end_time = datetime.datetime.now()
        return (exception, begin_time, end_time)

    def __cancel(self, execution, now):
        for (f, action) in execution.submitted.items():
            if f.cancel():
                self.__mark_action_canceled(execution, action, now)
                del execution.submitted[f]
        for action in execution.pending:
            self.__mark_action_canceled(execution, action, now)
        execution.pending.clear()

    def __wait(self, execution):
        waited = futures.wait(execution.submitted.keys(), return_when=futures.FIRST_COMPLETED)
        for f in waited.done:
            action = execution.submitted[f]
            del execution.submitted[f]
            (exception, begin_time, end_time) = f.result()
            if exception:
                self.__mark_action_failed(execution, action, begin_time, end_time)
                execution.exceptions.append(exception)
                execution.report.set_success(False)
            else:
                self.__mark_action_successful(execution, action, begin_time, end_time)

    @staticmethod
    def __mark_action_canceled(execution, action, cancel_time):
        execution.failed.add(action)
        execution.report.set_action_status(
            action,
            ExecutionReport.ActionStatus(
                ready_time=execution.submitted_at.get(action),
                cancel_time=cancel_time,
            )
        )

    @staticmethod
    def __mark_action_successful(execution, action, start_time, success_time):
        execution.succeeded.add(action)
        execution.report.set_action_status(
            action,
            ExecutionReport.ActionStatus(
                ready_time=execution.submitted_at[action],
                start_time=start_time,
                success_time=success_time,
            ),
        )

    @staticmethod
    def __mark_action_failed(execution, action, start_time, failure_time):
        execution.failed.add(action)
        execution.report.set_action_status(
            action,
            ExecutionReport.ActionStatus(
                ready_time=execution.submitted_at[action],
                start_time=start_time,
                failure_time=failure_time,
            )
        )


class Action(object):
    """
    The main class of ActionTree.
    An action to be started after all its dependencies are finished.
    Pass it to :func:`.execute`.

    This is a base class for your custom actions.
    You must define a ``def do_execute(self):`` method that performs the action.
    Its return value is ignored.
    If it raises and exception, it is captured and re-raised in a :exc:`CompoundException`.

    See also :class:`.ActionFromCallable` if you just want to create an action from a simple callable.
    """
    # @todo Add a note about printing anything in do_execute
    # @todo Add a note saying

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


class ActionFromCallable(Action):
    """
    An :class:`.Action` sub-class for the simple use-case of using a plain callable as an action.
    """

    def __init__(self, do_execute, label):
        """
        :param label: see :class:`.Action`.
        :param callable do_execute: the function to execute the action.
        """
        super(ActionFromCallable, self).__init__(label)
        self.__do_execute = do_execute

    def do_execute(self):
        self.__do_execute()


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
