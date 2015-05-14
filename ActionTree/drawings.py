# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import matplotlib.figure as mpl
import graphviz

from . import Action


# @todo Capture last execution in an immutable copy of the action.
# Currently "a.execute(); r = make_report(a); a.execute()" will modify (and invalidate if timing changes a lot) the report.
# Same for Graph? Yes if we implement the Graph class as suggested in following todo.
# Adding a new dependency would be reflected in the graph after its creation.


class ExecutionReport(object):
    def __init__(self, action):
        self.root_action = action
        self.actions = list(self.__sort_actions(action))
        self.begin_time = min(a.begin_time for a in self.actions)
        self.end_time = max(a.end_time for a in self.actions)
        self.duration = self.end_time - self.begin_time

    def __sort_actions(self, root):
        # @todo Handle diamond dependencies
        seen = set()

        def walk(action):
            if id(action) not in seen:
                seen.add(id(action))
                for d in sorted(action.dependencies, key=lambda d: d.end_time, reverse=True):
                    for a in walk(d):
                        yield a
                yield action

        return walk(root)


def make_report(action):  # pragma no cover (Untestable? But small.)
    """
    Build a :class:`matplotlib.figure.Figure` about the execution of the action,
    showing successes and failures as well as timing information.

    See also :func:`.plot_report` if you want to draw the report on your own matplotlib figure.
    """
    fig = mpl.Figure()
    ax = fig.add_subplot(1, 1, 1)

    plot_report(action, ax)

    return fig


def plot_report(action, ax):
    """
    Plot a report about the execution of the action,
    showing successes and failures as well as timing information on the provided :class:`matplotlib.axes.Axes`.
    """
    report = ExecutionReport(action)

    ordinates = {id(a): len(report.actions) - i for i, a in enumerate(report.actions)}

    for a in report.actions:
        if action.status == Action.Successful:
            style = "b-"
        else:
            style = "r-"
        ax.plot([a.begin_time, a.end_time], [ordinates[id(a)], ordinates[id(a)]], style, lw=4)
        for d in a.dependencies:
            ax.plot([d.end_time, a.begin_time], [ordinates[id(d)], ordinates[id(a)]], "k:", lw=1)

    ax.set_ylim(0.5, len(report.actions) + 0.5)


class GraphBuilder(object):
    def __init__(self, action):
        self.__nodes = dict()
        self.__next_node = 0
        self.graph = graphviz.Digraph("action", node_attr={"shape": "box"})
        self.__create_node(action)

    def __create_node(self, a):
        if id(a) not in self.__nodes:
            node = str(self.__next_node)
            label = str(a.label)
            self.graph.node(node, label)
            self.__next_node += 1
            for d in a.dependencies:
                self.graph.edge(node, self.__create_node(d))
            self.__nodes[id(a)] = node
        return self.__nodes[id(a)]


# @todo Should there be a class Graph with a method get_graphviz_graph?
# This would allow implementing graphs in other libraries without creating more free functions.
# Same for execution reports.


def make_graph(action, format="png"):
    """
    Build a :class:`graphviz.Digraph` representing the action and its dependencies.
    """
    g = GraphBuilder(action).graph
    g.format = format
    return g
