# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import datetime
import multiprocessing
import os.path
import pickle

import graphviz
import matplotlib
import matplotlib.dates
import matplotlib.figure
import matplotlib.backends.backend_agg
import wurlitzer


class Hooks(object):
    def action_pending(self, time, action):
        pass

    def action_ready(self, time, action):
        pass

    def action_canceled(self, time, action):
        pass

    def action_started(self, time, action):
        pass

    def action_printed(self, time, action, text):
        pass

    def action_successful(self, time, action):
        pass

    def action_failed(self, time, action):
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
    _check_picklability(action)
    if jobs is None:
        jobs = multiprocessing.cpu_count()
    return _Execution(jobs, keep_going, do_raise, hooks, action).run()


def _check_picklability(stuff):
    # This is a way to fail fast if we see a non-picklable object
    # because ProcessPoolExecutor freezes forever if we try to transfer
    # a non-picklable object through its queues
    pickle.loads(pickle.dumps(stuff))


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

        def __init__(self):
            self.__ready_time = None
            self.__cancel_time = None
            self.__start_time = None
            self.__success_time = None
            self.__return_value = None
            self.__failure_time = None
            self.__exception = None
            self.__output = None

        def _set_ready_time(self, ready_time):
            self.__ready_time = ready_time

        def _set_cancel_time(self, cancel_time):
            self.__cancel_time = cancel_time

        def _set_start_time(self, start_time):
            self.__start_time = start_time

        def _set_success(self, success_time, return_value):
            self.__success_time = success_time
            self.__return_value = return_value
            self._add_output("")

        def _set_failure(self, failure_time, exception):
            self.__failure_time = failure_time
            self.__exception = exception
            self._add_output("")

        def _add_output(self, output):
            self.__output = (self.__output or "") + output

        @property
        def status(self):
            """
            @todo Document
            """
            if self.start_time:
                if self.success_time:
                    return self.Successful
                else:
                    assert self.failure_time
                    return self.Failed
            else:
                assert self.cancel_time
                return self.Canceled

        @property
        def ready_time(self):
            """
            The local :class:`~datetime.datetime` when this action was ready to execute.
            """
            return self.__ready_time

        @property
        def cancel_time(self):
            """
            The local :class:`~datetime.datetime` when this action was canceled.
            """
            return self.__cancel_time

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
        def return_value(self):
            """
            @todo Document
            """
            return self.__return_value

        @property
        def failure_time(self):
            """
            The local :class:`~datetime.datetime` at the successful end of the execution of this action.
            """
            return self.__failure_time

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

    def __init__(self, actions):
        self.__action_statuses = {action: self.ActionStatus() for action in actions}

    @property
    def is_success(self):
        """
        ``True`` if the execution finished without error.

        :rtype: bool
        """
        return all(
            action_status.status == self.ActionStatus.Successful
            for action_status in self.__action_statuses.itervalues()
        )

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


class WurlitzerToEvents(wurlitzer.Wurlitzer):
    # This is a highly contrived use of Wurlitzer:
    # We just need to *capture* standards streams, so we trick Wurlitzer,
    # passing True instead of writeable file-like objects, and we redefine
    # _handle_xxx methods to intercept what it would write
    def __init__(self, events, action_id):
        super(WurlitzerToEvents, self).__init__(stdout=True, stderr=True)
        self.events = events
        self.action_id = action_id

    def _handle_stdout(self, data):
        self.events.put(_PrintedEvent(self.action_id, datetime.datetime.now(), self._decode(data)))

    def _handle_stderr(self, data):
        self._handle_stdout(data)


class _Worker(multiprocessing.Process):
    def __init__(self, action_id, action, events):
        multiprocessing.Process.__init__(self)
        self.action_id = action_id
        self.action = action
        self.events = events

    def run(self):
        with WurlitzerToEvents(self.events, self.action_id):
            return_value = exception = None
            try:
                self.events.put(_StartedEvent(self.action_id, datetime.datetime.now()))
                return_value = self.action.do_execute()
            except Exception as e:
                exception = e
        try:
            _check_picklability((exception, return_value))
        except:
            self.events.put(_PicklingExceptionEvent(self.action_id))
        else:
            end_time = datetime.datetime.now()
            if exception:
                self.events.put(_FailedEvent(self.action_id, end_time, exception))
            else:
                self.events.put(_SuccessedEvent(self.action_id, end_time, return_value))


class _Event(object):
    def __init__(self, action_id):
        self.action_id = action_id


class _StartedEvent(_Event):
    def __init__(self, action_id, start_time):
        super(_StartedEvent, self).__init__(action_id)
        self.start_time = start_time

    def apply(self, execution, action):
        execution.report.get_action_status(action)._set_start_time(self.start_time)
        execution.hooks.action_started(self.start_time, action)


class _SuccessedEvent(_Event):
    def __init__(self, action_id, success_time, return_value):
        super(_SuccessedEvent, self).__init__(action_id)
        self.success_time = success_time
        self.return_value = return_value

    def apply(self, execution, action):
        execution.submitted.remove(action)
        execution.successful.add(action)
        execution.report.get_action_status(action)._set_success(self.success_time, self.return_value)
        execution.hooks.action_successful(self.success_time, action)


class _PrintedEvent(_Event):
    def __init__(self, action_id, print_time, text):
        super(_PrintedEvent, self).__init__(action_id)
        self.print_time = print_time
        self.text = text

    def apply(self, execution, action):
        execution.report.get_action_status(action)._add_output(self.text)
        execution.hooks.action_printed(self.print_time, action, self.text)


class _FailedEvent(_Event):
    def __init__(self, action_id, failure_time, exception):
        super(_FailedEvent, self).__init__(action_id)
        self.failure_time = failure_time
        self.exception = exception

    def apply(self, execution, action):
        execution.submitted.remove(action)
        execution.failed.add(action)
        execution.exceptions.append(self.exception)
        execution.report.get_action_status(action)._set_failure(self.failure_time, self.exception)
        execution.hooks.action_failed(self.failure_time, action)


class _PicklingExceptionEvent(_Event):
    def apply(self, execution, action):
        raise pickle.PicklingError()


class _Execution(object):
    def __init__(self, jobs, keep_going, do_raise, hooks, action):
        self.events = multiprocessing.Queue()
        self.jobs = jobs
        self.keep_going = keep_going
        self.do_raise = do_raise
        self.hooks = hooks
        self.actions_by_id = {id(action): action for action in action.get_all_dependencies()}
        self.pending = set(self.actions_by_id.itervalues())
        self.submitted = set()
        self.successful = set()
        self.failed = set()
        self.exceptions = []
        self.report = ExecutionReport(self.pending)

    def run(self):
        now = datetime.datetime.now()
        for action in self.pending:
            self.hooks.action_pending(now, action)
        while self.pending or self.submitted:
            self._progress()

        for w in multiprocessing.active_children():
            w.join()

        if self.do_raise and self.exceptions:
            raise CompoundException(self.exceptions, self.report)
        else:
            return self.report

    def _progress(self):
        now = datetime.datetime.now()
        if self.keep_going or not self.exceptions:
            self._submit_or_cancel(now)
        else:
            self._cancel(now)
        self._wait()

    def _submit_or_cancel(self, now):
        go_on = True
        while go_on:
            go_on = False
            for action in set(self.pending):
                done = self.successful | self.failed
                if all(d in done for d in action.dependencies):
                    if any(d in self.failed for d in action.dependencies):
                        self._mark_action_canceled(action, cancel_time=now)
                        self.pending.remove(action)
                        go_on = True
                    else:
                        status = self.report.get_action_status(action)
                        if status.ready_time is None:
                            status._set_ready_time(now)
                            self.hooks.action_ready(now, action)
                        if len(self.submitted) <= self.jobs:
                            self._submit_action(action, ready_time=now)

    def _cancel(self, now):
        for action in self.pending:
            self._mark_action_canceled(action, cancel_time=now)
        self.pending.clear()

    def _wait(self):
        if self.submitted:
            event = self.events.get()
            event.apply(self, self.actions_by_id[event.action_id])

    def _submit_action(self, action, ready_time):
        _Worker(id(action), action, self.events).start()
        self.submitted.add(action)
        self.pending.remove(action)

    def _mark_action_canceled(self, action, cancel_time):
        self.failed.add(action)
        self.report.get_action_status(action)._set_cancel_time(cancel_time)
        self.hooks.action_canceled(cancel_time, action)


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

    # @todo Remove? (get_possible_execution_order does it already)
    def get_all_dependencies(self):
        """
        Return the set of this action's recursive dependencies, including itself.
        """
        dependencies = set([self])
        for dependency in self.__dependencies:
            dependencies |= dependency.get_all_dependencies()
        return dependencies

    # @todo Remove?
    def get_preview(self):
        """
        Return the labels of this action and its dependencies, in an order that could be the execution order.
        """
        return [action.__label for action in self.get_possible_execution_order()]

    def get_possible_execution_order(self, seen_actions=None):
        """
        @todo Document
        """
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
