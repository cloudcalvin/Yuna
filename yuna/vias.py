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


def add_layers(base, wire):
    """ Add the wire layers that are connected to the via. """

    wireoffset = tools.angusj_offset(wire.layer, 'up')
    return layers.does_layers_intersect([base], wireoffset)


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


def update_wire_object(wire, i, _id):
    """ V1 labeled edge is connected to Via 1.
    P1 is connected to Port 1. """
    
    wire.edgelabels[i] = 'V' + str(_id)


def fill_via_list(vias, atom):
    """ Copy the 'result' list in the vias
    Subatom to the self.vias list of
    via objects. """

    via_id = 0
    for subatom in atom['Subatom']:
        for poly in subatom['result']:
            via = Via(via_id, poly, subatom['gds'])
            vias.append(via)
            via_id += 1
            

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
        self.gds = gds
        self.edges = []

    def connect_wires(self, wire):
        if wire.active and wire.polygon:
            wireoffset = tools.angusj_offset(wire.polygon, 'up')
            if layers.does_layers_intersect([self.polygon], wireoffset):
                self.connect_edges(wire)

    def connect_edges(self, wire):
        for i, polygon in enumerate(wire.polygon):
            for point in polygon:
                inside = pyclipper.PointInPolygon(point, self.polygon)

                if inside != 0:
                    self.edges.append(point)
                    update_wire_object(wire, i, self.id)

    def plot_via(self, cell):
        cell.add(gdspy.Polygon(self.polygon, self.gds))

    def plot_connected_wires(self, cell):
        for gds, layers in self.wires.items():
            for poly in layers:
                cell.add(gdspy.Polygon(poly, gds))
                
                
                
                
                
                
                
                
