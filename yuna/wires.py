from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from .utils import tools

import json
import gdspy
import networkx as nx
import yuna.layers as layers


def union_polygons(Layers):
    """ Union the normal wiring polygons. """

    tools.green_print('Union Layer:')
    for key, layer in Layers.items():
        tools.union_wire(Layers, key)


class WireSet:
    """  """

    def __init__(self, gds, active=False):
        self.active = active
        self.gds = gds
        self.wires = []
        self.mesh = []
        self.graph = []

    def set_mesh(self, mesh):
        self.mesh = mesh

    def set_graph(self, graph):
        self.graph = graph

    def add_wire_object(self, wire):
        self.wires.append(wire)
        

def fill_wiresets(Layers, wiresets, union):
    """ Loop through the Layer object
    and save each layer as a wire object."""

    tools.green_print('Calculating wires json:')

    if union:
        union_polygons(Layers)

    tools.magenta_print('Active layers:')    
    for name, layers in Layers.items():
        if (layers['type'] == 'wire') or (layers['type'] == 'resistance') or (layers['type'] == 'shunt'):
            wireset = WireSet(layers['gds'])

            view = json.loads(layers['view'])
            print('  ' + name)
                
            for layer in layers['result']:
                # If it's a 2D list, make it a 3D list.
                if not isinstance(layer[0][0], list):
                    layer = [layer]

                if layer:
                    wire = Wire(layer, active=view)
                    wireset.add_wire_object(wire)

            wiresets[name] = wireset


class Wire:
    """  """

    def __init__(self, polygon, active=False):
        """  """

        self.active = active
        self.polygon = polygon
        self.lines = []

    def update_with_via_diff(self, vias):
        """ Connect vias and wires by finding
        their difference and not letting 
        the overlap. """

#         clip = []
#         for via in vias:
#             clip.append(via.polygon)
# 
#         wireoffset = tools.angusj_offset(clip, 'down')
# 
#         if layers.does_layers_intersect(self.polygon, wireoffset):
#             return True
#         else:
#             return False

        subj = self.polygon

        clip = []
        for via in vias:
            clip.append(via.polygon)
        
        update = False
        if clip and subj:
            self.polygon = tools.angusj(clip, subj, 'difference')

            if self.polygon:
                self.edgelabels = [None] * len(self.polygon[0])
                update = True

#         return update

    def update_with_jj_diff(self, jjs):
        """ Find the difference between the wiring
        polygons and the junction base polygons. """

        subj = self.polygon

        clip = []
        for jj in jjs:
            clip.append(jj.polygon)

        if clip and subj:
            self.polygon = tools.angusj(clip, subj, 'difference')
            self.edgelabels = [None] * len(self.polygon)
            print(self.polygon)
            print(len(self.polygon))

    def plot_wire(self, cell, gds):
        if self.active:
            for poly in self.polygon:
                cell.add(gdspy.Polygon(poly, gds))
                
                
                
                
                
                
                
                
                
