from __future__ import print_function
from termcolor import colored
from utils import tools
 
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

import gdspy
import layers
import pyclipper


def get_polygon(Layers, Modules, poly):
    """  """

    polyclass = poly.keys()[0]
    polylayer = poly.values()[0]

    subjclip = None
    if polyclass == 'Layer':
        subjclip = Layers[polylayer]['result']
    elif polyclass == 'Module':
        subjclip = Modules[polylayer]['result']

    return subjclip


def get_layercross(Layers, Modules, value):
    """ Intersect the layers in the 'clip' object
    in the submodule. """

    subj = get_polygon(Layers, Modules, value['wire_1'])
    clip = get_polygon(Layers, Modules, value['wire_2'])

    layercross = []
    if subj and clip:
        layercross = tools.angusj(clip, subj, 'intersection')
        if not layercross:
            print('Clipping is zero.')

    return layercross


def add_layers(base, wire):
    """ Add the wire layers that are
    connected to the via. """

    poly_list = []

    for poly in wire.layer:
        wireoffset = tools.angusj_offset([poly], 'up')

        if layers.does_layers_intersect([base], wireoffset):
            poly_list.append(poly)

    return poly_list


def get_viacross(Layers, Modules, value, subj):
    """  """

    clip = get_polygon(Layers, Modules, value['via_layer'])

    result_list = []
    viacross = []
    for poly in subj:
        result_list = tools.angusj([poly], clip, "intersection")
        if result_list:
            viacross.append(poly)

    return viacross


def reverse_via(Layers, Modules, value, subj):
    """ This method is called when we have
    to save the via as the first layer below
    it. This is needed when the crossings 
    of the two wiring layers are not equally large.

    Note
    ----
    Note that wire_1 must be the largest polygon.
    """

    clip = get_polygon(Layers, Modules, value['wire_1'])

    result_list = []
    wireconnect = []
    for poly in clip:
        result_list = tools.angusj([poly], subj, 'intersection')
        if result_list:
            wireconnect.append(poly)

    return wireconnect


def remove_viacross(Layers, Modules, value):
    """  """

    subj = get_polygon(Layers, Modules, value['wire_1'])
    clip = get_polygon(Layers, Modules, value['via_layer'])

    result_list = []
    viacross = []
    for poly in subj:
        result_list = tools.angusj([poly], clip, "intersection")
        if not result_list:
            viacross.append(poly)

    return viacross


class Via:
    """
    """

    def __init__(self):
        """
        Variables
        ---------
        edges : list
            List of the edges connected to the via.
        base : list
            The base polygon that defineds the via.
        gds : int
            The GDS number in the Module in JSON
            that defines the via.
        wires : list
            Dict of 'wire' objects that are connected
            to the via. The 'edge' variable contains
            the edges of these wire layers connected 
            to the via.

        Note
        ----
        * Not all layers in a wire object is connected 
          to the via. Therefore, self.wires.key is the 
          wire.gds and the value is the polygons connected.
        """

        self.edges = {}
        self.base = []
        self.gds = 0
        self.wires = {}


#     Maybe give access to select a specific 
#     via or viaset (kind, like viaMN1_M2).

    def set_base(self, poly):
        self.base = poly

    def set_gds(self, num):
        self.gds = num

    def connect_wires(self, wires):
        for wire in wires:
            if wire.active:
               poly_list = add_layers(self.base, wire)
               self.wires[wire.gds] = poly_list

    def connect_edges(self):
        for gds, layer in self.wires.items():
            if layer:
                self.edges[gds] = []
                for point in layer[0]:
                    inside = pyclipper.PointInPolygon(point, self.base)

                    if inside != 0:
                        self.edges[gds].append(point)
#                         self.edges.append(point)

    def plot_via(self, cell):
        cell.add(gdspy.Polygon(self.base, self.gds))

    # TODO: Maybe add the debug verbose option here.
    def plot_connected_wires(self, cell):
        for gds, layers in self.wires.items():
            for poly in layers:
                cell.add(gdspy.Polygon(poly, gds))

    def generate_graph(self):
        g = nx.Graph()

        g.add_node(1, pos=self.base[0])
        g.add_node(2, pos=self.base[1])
        g.add_node(3, pos=self.base[2])
        g.add_node(4, pos=self.base[3])

        g.add_edge(1,2)
        g.add_edge(2,3)
        g.add_edge(3,4)
        g.add_edge(4,1)

        pos = nx.get_node_attributes(g,'pos')

        nx.draw(g, pos)

    def plot_edges(self):
        verts = [
            (0., 0.), # left, bottom
            (0., 1.), # left, top
            (1., 1.), # right, top
            (1., 0.), # right, bottom
            (0., 0.), # ignored
            ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.CLOSEPOLY,
                 ]

        path = Path(verts, codes)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        patch = patches.PathPatch(path, facecolor='orange', lw=2)
        ax.add_patch(patch)
        ax.set_xlim(-2,2)
        ax.set_ylim(-2,2)
        plt.show()

#         vertices = []
#         codes = []
# 
#         codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
#         vertices = [(1, 1), (1, 2), (2, 2), (2, 1), (0, 0)]
# 
#         codes += [Path.MOVETO] + [Path.LINETO]*2 + [Path.CLOSEPOLY]
#         vertices += [(4, 4), (5, 5), (5, 4), (0, 0)]
# 
#         vertices = np.array(vertices, float)
#         path = Path(vertices, codes)
# 
#         pathpatch = PathPatch(path, facecolor='None', edgecolor='green')
# 
#         fig, ax = plt.subplots()
#         ax.add_patch(pathpatch)
#         ax.set_title('A compound path')
# 
#         ax.dataLim.update_from_data_xy(vertices)
#         ax.autoscale_view()
# 
#         plt.show()









