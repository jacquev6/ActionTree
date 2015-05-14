# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

import matplotlib.figure as mpl
import graphviz


def make_report(action):
    """
    Build a :class:`matplotlib.figure.Figure` about the execution of the action,
    showing successes and failures as well as timing information.
    """
    fig = mpl.Figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2.5, 3], [4, 5, 6])
    ax.set_title('hi mom')
    ax.grid(True)
    ax.set_xlabel('time')
    ax.set_ylabel('volts')
    return fig


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
