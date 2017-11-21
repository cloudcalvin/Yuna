from __future__ import print_function

from termcolor import colored
from .utils import tools


import gdspy
import networkx as nx


def union_polygons(Layers):
    """ Union the normal wiring polygons. """

    tools.green_print('Union Layer:')
    for key, layer in Layers.items():
        tools.union_wire(Layers, key, 'result')


class WireSet:
    """

    """

    def __init__(self, name, gds, active=False):
        self.active = active
        self.gds = gds
        self.name = name
        self.wires = []
        self.mesh = {}
        self.graph = None

        self.mesh['points'] = []
        self.mesh['cells'] = []

    def set_mesh(self, mesh):
        self.mesh = mesh

    def set_graph(self, graph):
        self.graph = graph

    def add_wire_object(self, wire):
        self.wires.append(wire)


class Wire:
    """
    """

    def __init__(self, points, active=False):
        """  """

        self.active = active
        self.points = points
        self.edgelabels = [None] * len(points[0])

    def update_with_via_diff(self, vias):
        """ Connect vias and wires by finding
        their difference and not letting the overlap. """

        subj = self.points

        clip = []
        for via in vias:
            clip.append(via.base)

        if clip and subj:
            self.points = tools.angusj(clip, subj, 'difference')

    def update_with_jj_diff(self, jjs):
        """ Find the difference between the wiring
        polygons and the junction base polygons. """

        subj = self.points

        clip = []
        for jj in jjs:
            clip.append(jj.base)

        if clip and subj:
            self.points = tools.angusj(clip, subj, 'difference')

    # def generate_graph(self):
    #     for poly in self.layer:
    #         g = nx.Graph()
    #         num_nodes = len(poly)
    #
    #         for i, node in enumerate(poly):
    #             g.add_node(i, pos=node)
    #
    #             if i < num_nodes-1:
    #                 g.add_edge(i, i+1)
    #             else:
    #                 g.add_edge(i, 0)
    #
    #         for n, p in g.nodes(data=True):
    #             print(p['pos'])
    #
    #         pos = nx.get_node_attributes(g,'pos')
    #         nx.draw(g, pos, node_size=30)

    def plot_wire(self, cell, gds):
        if self.active:
            for poly in self.points:
                cell.add(gdspy.Polygon(poly, gds))
