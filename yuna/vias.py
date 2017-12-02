from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from yuna.utils import tools

from matplotlib.path import Path
from matplotlib.patches import PathPatch

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

import gdspy
import yuna.layers as layers
import pyclipper
import yuna.wires as wires


def get_polygon(Layers, Modules, poly):
    """  """

    polyclass = list(poly.keys())[0]
    polylayer = list(poly.values())[0]

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


def get_viacross(Layers, Modules, value, subj):
    """  """

    clip = get_polygon(Layers, Modules, value['via_layer'])

    result_list = []
    viacross = []
    for poly in subj:
        if tools.angusj([poly], clip, "intersection"):
            viacross.append(poly)

    return viacross


def reverse_via(Layers, Modules, value, subj):
    """ 
    This method is called when we have
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


def update_edgelabels(wire, i, _id):
    """ V1 labeled edge is connected to Via 1.
    P1 is connected to Port 1. """
    
    label = 'V' + str(_id)
    wire.edgelabels.append(label)


# def is_via_cell(element):
#     """  """

#     viabool = False
    
#     if isinstance(element, gdspy.CellReference):
#         print('      CellReference: ', end='')
#         print(element)
#         refname = element.ref_cell.name
#         if refname[:2] == 'JJ':
#             viabool = True

#     return viabool


# def fill_via_list(config, basedir, vias):
#     """ Loop over all elements, such as
#     polygons, polgyonsets, cellrefences, etc
#     and find the CellRefences. CellRefs
#     which is a junction has to start with JJ. """
    
#     atom = config.Atom['vias']

#     via_id = 0
#     for element in config.Elements:
#         if is_via_cell(element):
#             layers = transpose_cell(config.gdsii, config.Layers, element)

#             via = Junction(basedir, jj_id, config.Layers)
#             via.set_layers(layers)
#             via.detect_jj(atom)
#             vias.append(jj)
#             via_id += 1


# https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python
def line_intersection(line1, line2):    
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    return x, y


def fill_via_list(vias, atom):
    """ Copy the 'result' list in the vias
    Subatom to the self.vias list of
    via objects. """

    via_id = 0
    for subatom in atom['Subatom']:
        for poly in subatom['result']:
            via = Via(via_id, poly, subatom['gds'])
            via.convert_polygon_to_lines()

            vias.append(via)
            via_id += 1


def get_line_orientation(p1, p2):
    if p1[0] - p2[0] == 0.0:
        return 'y'
    if p1[1] - p2[1] == 0.0:
        return 'x'


def make_edge_polygon(p1, p2):
    if get_line_orientation(p1, p2) == 'x':
        pt1 = [None] * 2
        pt2 = [None] * 2
        pb1 = [None] * 2
        pb2 = [None] * 2

        pt1[0] = p1[0]
        pt1[1] = p1[1] + 10

        pt2[0] = p2[0]
        pt2[1] = p2[1] + 10

        pb1[0] = p1[0]
        pb1[1] = p1[1] - 10

        pb2[0] = p2[0]
        pb2[1] = p2[1] - 10

        return [pt1, pt2, pb2, pb1]

    elif get_line_orientation(p1, p2) == 'y':
        pt1 = [None] * 2
        pt2 = [None] * 2
        pb1 = [None] * 2
        pb2 = [None] * 2

        pt1[0] = p1[0] + 10
        pt1[1] = p1[1]

        pt2[0] = p2[0] + 10
        pt2[1] = p2[1]

        pb1[0] = p1[0] - 10
        pb1[1] = p1[1]

        pb2[0] = p2[0] - 10
        pb2[1] = p2[1]

        return [pt1, pt2, pb2, pb1]
            

class Via:
    def __init__(self, via_id, polygon, gds):
        """
        Variables
        ---------
        edges : list
            List of the edges connected to the via.
        polygon : list
            The base polygon that defines the via.
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

        self.id = via_id
        self.polygon = polygon
        self.lines = []
        self.gds = gds
        self.edges = []

    def convert_polygon_to_lines(self):
        for i in range(len(self.polygon) - 1):
            p1 = wires.Point(self.polygon[i][0], self.polygon[i][1])
            p2 = wires.Point(self.polygon[i+1][0], self.polygon[i+1][1])

            line = wires.Line()

            line.add_point(p1)
            line.add_point(p2)


    def connect_wires(self, wire):
        if wire.active and wire.polygon:
            wireoffset = tools.angusj_offset(wire.polygon, 'up')
            if layers.does_layers_intersect([self.polygon], wireoffset):
                self.connect_edges(wire)

    def connect_edges(self, wire):
        tools.green_print('edges:')

        for i in range(len(self.polygon) - 1):
            pw1 = self.polygon[i]
            pw2 = self.polygon[i+1]

            edgepoly = make_edge_polygon(pw1, pw2)
            print('poly')
            print(edgepoly)

            for j, wirepoly in enumerate(wire.polygon):
                if layers.does_layers_intersect([edgepoly], [wirepoly]):
                    update_edgelabels(wire, j, self.id)

        pw1 = self.polygon[-1]
        pw2 = self.polygon[0]

        edgepoly = make_edge_polygon(pw1, pw2)
        print('poly')
        print(edgepoly)

        for j, wirepoly in enumerate(wire.polygon):
            if layers.does_layers_intersect([edgepoly], [wirepoly]):
                update_edgelabels(wire, j, self.id)



            # for j in range(len(wire.polygon) - 1):
            #     pp1 = wire.polygon[j]
            #     pp2 = wire.polygon[j+1]


            # for point in polygon:
            #     inside = pyclipper.PointInPolygon(point, self.polygon)

            #     if inside != 0:
            #         self.edges.append(point)
            #         update_edgelabels(wire, i, self.id)

    def plot_via(self, cell):
        cell.add(gdspy.Polygon(self.polygon, self.gds))

    def plot_connected_wires(self, cell):
        for gds, layers in self.wires.items():
            for poly in layers:
                cell.add(gdspy.Polygon(poly, gds))
                
                
                
                
                
                
                
                
