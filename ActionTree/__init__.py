# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

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


def execute(action, cpu_cores=None, keep_going=False, do_raise=True, hooks=None):
    """
    Recursively execute an :class:`.Action`'s dependencies then the action.

    :param Action action: the action to execute.
    :param cpu_cores: number of CPU cores to use in parallel.
        Pass ``None`` (the default value) to let ActionTree choose.
        Pass :attr:`UNLIMITED` to execute an unlimited number of actions in parallel
        (make sure your system has the necessary resources).
        Note: CPU cores are managed like any other :class:`Resource`, and this parameter sets the availability
        of :obj:`CPU_CORE` for this execution.
    :type cpu_cores: int or None or UNLIMITED
    :param bool keep_going: if ``True``, then execution does not stop on first failure,
        but executes as many dependencies as possible.
    :param bool do_raise: if ``False``, then exceptions are not re-raised as :exc:`CompoundException`
        but only included in the :class:`.ExecutionReport`.
    :param Hooks hooks: its methods will be called when execution progresses.

    :raises CompoundException: when ``do_raise`` is ``True`` and dependencies raise exceptions.

    :rtype: ExecutionReport
    """
    if cpu_cores is None:
        cpu_cores = multiprocessing.cpu_count()
    if hooks is None:
        hooks = Hooks()
    return _Execute(cpu_cores, keep_going, do_raise, hooks).run(action)


UNLIMITED = object()
"""The availability of an infinite :class:`Resource`."""


class Action(object):
    """
    The main class of ActionTree.
    An action to be started after all its dependencies are finished.
    Pass it to :func:`.execute`.

    This is a base class for your custom actions.
    You must define a ``do_execute(self, dependency_statuses)`` method that performs the action.
    The ``dependency_statuses`` argument is a dictionary whose keys are ``self.dependencies`` and values are their
    :class:`.ActionStatus`.
    :ref:`outputs` describes how its return values, the exceptions it may raise and what it may print is handled.

    Actions, return values and exceptions raised must be picklable.
    """

    def __init__(self, label, weak_dependencies=False):
        """
        :param label: whatever you want to attach to the action.
            ``str(label)`` must succeed and return a string.
            Can be retrieved by :attr:`label`.
        :param bool weak_dependencies:
            it ``True``, then the action will execute even if some of its dependencies failed.
        """
        str(label)
        self.__label = label
        self.__weak_dependencies = weak_dependencies
        self.__dependencies = []
        self.__resources = {CPU_CORE: 1}

    @property
    def label(self):
        """
        The label passed to the constructor.
        """
        return self.__label

    @property
    def weak_dependencies(self):
        """
        ``True`` if the action will execute even if some of its dependencies failed.

        :rtype: bool
        """
        return self.__weak_dependencies

    def add_dependency(self, dependency):
        """
        Add a dependency to be executed before this action.
        Order of insertion of dependencies is not important.

        :param Action dependency:

        :raises DependencyCycleException: when adding the new dependency would create a cycle.
        """
        if self in dependency.get_possible_execution_order():  # Not in user guide: implementation detail
            raise DependencyCycleException()
        self.__dependencies.append(dependency)

    @property
    def dependencies(self):
        """
        The list of this action's direct dependencies.
        """
        return list(self.__dependencies)

    def require_resource(self, resource, quantity=1):
        """
        Set the quantity of a certain :class:`.Resource` required to run this action.

        Note that an action that requires more than a resource's availability *will* be executed anyway.
        It will just not be executed in parallel with any other action that requires the same resource.

        :param Resource resource:
        :param int quantity:
        """
        self.__resources[resource] = quantity

    @property
    def resources_required(self):
        """
        The list of this action's required resources and quantities required.

        :rtype: list(tuple(Resource, int))
        """
        return list(self.__resources.iteritems())

    def get_possible_execution_order(self, seen_actions=None):
        """
        Return the list of all this action's dependencies (recursively),
        in an order that is suitable for linear execution.
        Note that this order is not unique.
        The order chosen is not specified.
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


class Resource(object):
    """
    A resource that an :class:`Action` can require for its execution.
    You can use resources to protect stuff that must not be used by more than N actions at the same time,
    à la `semaphore <https://en.wikipedia.org/wiki/Semaphore_(programming)>`_.
    Like semaphorees, with an availability of 1,
    they become `mutexes <https://en.wikipedia.org/wiki/Lock_(computer_science)>`_.

    :ref:`resources` Describes how to use this class.
    """

    def __init__(self, availability):
        """
        :param availability: the number of instances available for this resource
        :type availability: int or UNLIMITED
        """
        self.__availability = availability

    def _availability(self, cpu_cores):
        return self.__availability


class CpuCoreResource(Resource):
    def _availability(self, cpu_cores):
        return cpu_cores


CPU_CORE = CpuCoreResource(0)
"""
A special :class:`.Resource` representing a processing unit.
You can pass it to :meth:`.Action.require_resource` if your action will execute on more than one core.

:type: Resource
"""


class Hooks(object):
    """
    Base class to derive from when defining your hooks.
    :func:`.execute` will call its methods when execution progresses.
    """
    def action_pending(self, time, action):
        """
        Called when an action is considered for execution, i.e. at the beginning of :func:`.execute`.

        :param datetime.datetime time: the time at which the action was considered for execution.
        :param Action action: the action.
        """

    def action_ready(self, time, action):
        """
        Called when an action is ready to be executed, i.e. when all its dependencies have succeeded.

        :param datetime.datetime time: the time at which the action was ready.
        :param Action action: the action.
        """

    def action_canceled(self, time, action):
        """
        Called when an action's execution is canceled, i.e. when some of its dependencies has failed.

        :param datetime.datetime time: the time at which the action was canceled.
        :param Action action: the action.
        """

    def action_started(self, time, action):
        """
        Called when an action's execution starts.

        :param datetime.datetime time: the time at which the action was started.
        :param Action action: the action.
        """

    def action_printed(self, time, action, text):
        """
        Called when an action prints something.

        :param datetime.datetime time: the time at which the action printed the text.
        :param Action action: the action.
        :param str text: the text printed.
        """

    def action_successful(self, time, action, return_value):
        """
        Called when an action completes without error.

        :param datetime.datetime time: the time at which the action completed.
        :param Action action: the action.
        :param return_value: the value returned by the action.
        """

    def action_failed(self, time, action, exception):
        """
        Called when an action completes with an exception.

        :param datetime.datetime time: the time at which the action completed.
        :param Action action: the action.
        :param exception: the exception raised by the action
        """


class DependencyCycleException(Exception):  # Not in user guide: implementation detail
    """
    Exception thrown by :meth:`.Action.add_dependency` when adding the new dependency would create a cycle.
    """

    def __init__(self):
        super(DependencyCycleException, self).__init__("Dependency cycle")


class CompoundException(Exception):
    """
    Exception thrown by :func:`.execute` when dependencies raise exceptions.
    """

    def __init__(self, exceptions, execution_report):
        super(CompoundException, self).__init__(exceptions)
        self.__exceptions = exceptions
        self.__execution_report = execution_report

    @property
    def exceptions(self):
        """
        The list of exceptions raised.
        """
        return self.__exceptions

    @property
    def execution_report(self):
        """
        The :class:`.ExecutionReport` of the failed execution.
        """
        return self.__execution_report


class ExecutionReport(object):
    """
    ExecutionReport()

    Execution report, returned by :func:`.execute`.
    """

    class ActionStatus(object):
        """
        Status of a single :class:`.Action`.
        """

        def __init__(self, pending_time):
            self.__pending_time = pending_time
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
            The status of the action:
            :attr:`SUCCESSFUL` if the action succeeded,
            :attr:`FAILED` if the action failed,
            and :attr:`CANCELED` if the action was canceled because some of its dependencies failed.
            """
            if self.start_time:
                if self.success_time:
                    return SUCCESSFUL
                else:
                    assert self.failure_time
                    return FAILED
            else:
                assert self.cancel_time
                return CANCELED

        @property
        def pending_time(self):
            """
            The time when this action was considered for execution.

            :rtype: datetime.datetime
            """
            return self.__pending_time

        @property
        def ready_time(self):
            """
            The time when this action was ready to execute.
            (``None`` if it was canceled before being ready).

            :rtype: datetime.datetime or None
            """
            return self.__ready_time

        @property
        def cancel_time(self):
            """
            The time when this action was canceled.
            (``None`` if it was started).

            :rtype: datetime.datetime or None
            """
            return self.__cancel_time

        @property
        def start_time(self):
            """
            The time at the beginning of the execution of this action.
            (``None`` if it was never started).

            :rtype: datetime.datetime or None
            """
            return self.__start_time

        @property
        def success_time(self):
            """
            The time at the successful end of the execution of this action.
            (``None`` if it was never started or if it failed).

            :rtype: datetime.datetime or None
            """
            return self.__success_time

        @property
        def return_value(self):
            """
            The value returned by this action
            (``None`` if it failed or was never started).
            """
            return self.__return_value

        @property
        def failure_time(self):
            """
            The time at the successful end of the execution of this action.
            (``None`` if it was never started or if it succeeded).

            :rtype: datetime.datetime or None
            """
            return self.__failure_time

        @property
        def exception(self):
            """
            The exception raised by this action
            (``None`` if it succeeded or was never started).
            """
            return self.__exception

        @property
        def output(self):
            """
            Everything printed (and flushed in time) by this action.
            (``None`` if it never started, ``""`` it if didn't print anything)

            :rtype: str or None
            """
            return self.__output

    def __init__(self, root_action, actions, now):
        self._root_action = root_action
        self.__action_statuses = {action: self.ActionStatus(now) for action in actions}

    @property
    def is_success(self):
        """
        ``True`` if the execution finished without error.

        :rtype: bool
        """
        return all(
            action_status.status == SUCCESSFUL
            for action_status in self.__action_statuses.itervalues()
        )

    def get_action_status(self, action):
        """
        Get the :class:`ActionStatus` of an action.

        :param Action action:

        :rtype: ActionStatus
        """
        return self.__action_statuses[action]

    def get_actions_and_statuses(self):
        """
        Get a list of actions and their statuses.

        :rtype: list(tuple(Action, ActionStatus))
        """
        return self.__action_statuses.items()


SUCCESSFUL = "SUCCESSFUL"
"The :attr:`.ActionStatus.status` after a successful execution."

FAILED = "FAILED"
"The :attr:`.ActionStatus.status` after a failed execution where this action raised an exception."

CANCELED = "CANCELED"
"The :attr:`.ActionStatus.status` after a failed execution where a dependency raised an exception."

PRINTED = "PRINTED"

PICKLING_EXCEPTION = "PICKLING_EXCEPTION"


class DependencyGraph(object):
    """
    A visual representation of the dependency graph, using `Graphviz <http://graphviz.org/>`__.
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

    def write_to_png(self, filename):  # Not unittested: too difficult
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


class GanttChart(object):  # Not unittested: too difficult
    """
    A visual representation of the timing of an execution.
    """

    def __init__(self, report):
        self.__actions = {
            id(action): self.__make_action(action, status)
            for (action, status) in report.get_actions_and_statuses()
        }

        self.__ordinates = {}

        dependents = {}
        for (action, _) in report.get_actions_and_statuses():
            dependents.setdefault(action, set())
            for dependency in action.dependencies:
                dependents.setdefault(dependency, set()).add(action)

        def compute(action, ordinate):
            self.__ordinates[id(action)] = len(self.__actions) - ordinate
            for d in sorted(
                action.dependencies,
                key=lambda d: report.get_action_status(d).success_time or report.get_action_status(d).failure_time
            ):
                if len(dependents[d]) == 1:
                    ordinate = compute(d, ordinate - 1)
                else:
                    dependents[d].remove(action)
            return ordinate

        last_ordinate = compute(report._root_action, len(self.__actions) - 1)
        assert last_ordinate == 0, last_ordinate

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
            ax.plot(
                [self.__start_time, self.__success_time], [ordinate, ordinate],
                color="blue", lw=4, solid_capstyle="butt",
            )
            # @todo Make sure the text is not outside the plot on the right
            ax.annotate(
                self.__label,
                xy=(self.__start_time, ordinate), xytext=(0, 3), textcoords="offset points",
            )
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
            ax.plot(
                [self.__start_time, self.__failure_time], [ordinate, ordinate],
                color="red", lw=4, solid_capstyle="butt",
            )
            ax.annotate(
                self.__label,
                xy=(self.__start_time, ordinate), xytext=(0, 3), textcoords="offset points",
            )
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
            if self.__ready_time:  # Not in user guide: implementation detail
                ax.plot([self.__ready_time, self.__cancel_time], [ordinate, ordinate], color="grey", lw=1)
            ax.annotate(
                self.__label,
                xy=(self.__cancel_time, ordinate), xytext=(0, 3), textcoords="offset points",
                color="grey",
            )
            for d in self.__dependencies:
                ax.plot([actions[d].max_time, self.min_time], [ordinates[d], ordinate], "k:", lw=1)

    @classmethod
    def __make_action(cls, action, status):
        if status.status == SUCCESSFUL:
            return cls.SuccessfulAction(action, status)
        elif status.status == FAILED:
            return cls.FailedAction(action, status)
        elif status.status == CANCELED:
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
    def __nearest(v, values):  # Not in user guide: implementation detail
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
        for action in self.__actions.itervalues():
            action.draw(ax, self.__ordinates, self.__actions)

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
        self.events.put((PRINTED, self.action_id, (datetime.datetime.now(), self._decode(data))))

    def _handle_stderr(self, data):
        self._handle_stdout(data)


class _Execute(object):
    def __init__(self, cpu_cores, keep_going, do_raise, hooks):
        self.cpu_cores = cpu_cores
        self.keep_going = keep_going
        self.do_raise = do_raise
        self.hooks = hooks

    def run(self, root_action):
        now = datetime.datetime.now()

        # Pre-process actions
        self._check_picklability(root_action)
        actions = root_action.get_possible_execution_order()
        self.actions_by_id = {id(action): action for action in actions}
        self.dependents = {action: set() for action in actions}
        for action in actions:
            for dependency in action.dependencies:
                self.dependents[dependency].add(action)

        # Misc stuff
        self.report = ExecutionReport(root_action, actions, now)
        for action in actions:
            self.hooks.action_pending(now, action)
        self.events = multiprocessing.Queue()
        self.exceptions = []
        self.resources_used = {}

        # Actions by status
        self.pending = set(actions)
        self.ready = set()
        self.running = set()
        self.done = set()
        for action in actions:
            if not action.dependencies:
                self._prepare_action(action, now)

        # Execute
        while self.pending or self.ready or self.running:
            self._progress(now)
            now = datetime.datetime.now()

        for w in multiprocessing.active_children():
            w.join()

        if self.do_raise and self.exceptions:
            raise CompoundException(self.exceptions, self.report)
        else:
            return self.report

    def _cancel_action(self, action, now):
        self.report.get_action_status(action)._set_cancel_time(now)
        self.hooks.action_canceled(now, action)

        if action in self.pending:
            self._change_status(action, self.pending, self.done)
        else:  # Not in user guide: implementation detail
            self._change_status(action, self.ready, self.done)

        if not self.keep_going:
            for d in action.dependencies:
                if d in self.pending or d in self.ready:
                    self._cancel_action(d, now)
        self._triage_pending_dependents(action, True, now)

    def _triage_pending_dependents(self, action, failed, now):
        for dependent in self.pending & self.dependents[action]:
            if failed and not dependent.weak_dependencies:
                self._cancel_action(dependent, now)
            elif all(d in self.done for d in dependent.dependencies):
                self._prepare_action(dependent, now)

    def _prepare_action(self, action, now):
        self.report.get_action_status(action)._set_ready_time(now)
        self.hooks.action_ready(now, action)

        self._change_status(action, self.pending, self.ready)

    def _progress(self, now):
        # @todo Should we tweak the scheduling?
        # We could prioritize the actions that use many resources,
        # hoping that this would avoid idle CPU cores at the end of the execution.
        # Scheduling is a hard problem, we may just want to keep the current, random, behavior.
        for action in set(self.ready):
            if self._allocate_resources(action):
                self._start_action(action, now)
        self._handle_next_event()

    def _allocate_resources(self, action):
        for (resource, quantity) in action.resources_required:
            used = self.resources_used.setdefault(resource, 0)
            if used == 0:
                # Allow actions requiring more than available to run when they are alone requiring this resource
                continue
            availability = resource._availability(self.cpu_cores)
            if availability is UNLIMITED:  # Not in user guide: implementation detail
                # Don't check usage of unlimited resources
                continue
            if used + quantity > availability:
                return False
        for (resource, quantity) in action.resources_required:
            self.resources_used[resource] += quantity
        return True

    def _start_action(self, action, now):
        self.report.get_action_status(action)._set_start_time(now)
        self.hooks.action_started(now, action)

        dependency_statuses = {d: self.report.get_action_status(d) for d in action.dependencies}
        p = multiprocessing.Process(
            target=self._run_action,
            kwargs=dict(action=action, action_id=id(action), dependency_statuses=dependency_statuses)
        )
        p.start()
        self._change_status(action, self.ready, self.running)

    def _run_action(self, action, action_id, dependency_statuses):
        with WurlitzerToEvents(self.events, action_id):
            return_value = exception = None
            try:
                return_value = action.do_execute(dependency_statuses)
            except Exception as e:
                exception = e
        try:
            self._check_picklability((exception, return_value))
        except:  # Not in user guide: mandatory picklability is more an issue than a feature
            self.events.put((PICKLING_EXCEPTION, action_id, ()))
        else:
            end_time = datetime.datetime.now()
            if exception:
                self.events.put((FAILED, action_id, (end_time, exception)))
            else:
                self.events.put((SUCCESSFUL, action_id, (end_time, return_value)))

    def _check_picklability(self, stuff):
        # This is a way to fail fast if we see a non-picklable object
        # because ProcessPoolExecutor freezes forever if we try to transfer
        # a non-picklable object through its queues
        pickle.loads(pickle.dumps(stuff))

    def _handle_next_event(self):
        (event_kind, action_id, event_payload) = self.events.get()
        handlers = {
            SUCCESSFUL: self._handle_successful_event,
            PRINTED: self._handle_printed_event,
            FAILED: self._handle_failed_event,
            PICKLING_EXCEPTION: self._handle_pickling_exception_event,
        }
        handlers[event_kind](self.actions_by_id[action_id], *event_payload)

    def _handle_successful_event(self, action, success_time, return_value):
        self.report.get_action_status(action)._set_success(success_time, return_value)
        self.hooks.action_successful(success_time, action, return_value)

        self._change_status(action, self.running, self.done)
        self._triage_pending_dependents(action, False, success_time)
        self._deallocate_resources(action)

    def _handle_printed_event(self, action, print_time, text):
        self.report.get_action_status(action)._add_output(text)
        self.hooks.action_printed(print_time, action, text)

    def _handle_failed_event(self, action, failure_time, exception):
        self.report.get_action_status(action)._set_failure(failure_time, exception)
        self.hooks.action_failed(failure_time, action, exception)

        self._change_status(action, self.running, self.done)
        self.exceptions.append(exception)
        self._triage_pending_dependents(action, True, failure_time)
        self._deallocate_resources(action)

    def _handle_pickling_exception_event(self, action):  # Not in user guide: mandatory picklability
        raise pickle.PicklingError()

    def _change_status(self, action, orig, dest):
        orig.remove(action)
        dest.add(action)

    def _deallocate_resources(self, action):
        for (resource, quantity) in action.resources_required:
            self.resources_used[resource] = max(0, self.resources_used[resource] - quantity)
