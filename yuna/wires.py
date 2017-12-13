from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from .utils import tools

import json
import gdspy
import pyclipper
import networkx as nx
import yuna.layers as layers
from collections import defaultdict


# def union_wire(Layers, layer):
#     """ This function saves the union of each
#     individual layer polygon. The result
#     is saved in the 'result' variable
#     in the config.json file of the
#     corrisponding layer. """

#     print('      -> ' + layer)

#     count = [0]
#     union_poly = defaultdict(list)

#     cell_layer = Layers[layer]['result']

#     for poly in cell_layer:
#         if (count[0] == 0):
#             union_poly[layer] = [poly]
#         else:
#             clip = poly
#             pc = pyclipper.Pyclipper()

#             pc.AddPath(clip, pyclipper.PT_CLIP, True)
#             pc.AddPaths(union_poly[layer], pyclipper.PT_SUBJECT, True)

#             union_poly[layer] = pc.Execute(pyclipper.CT_UNION,
#                                            pyclipper.PFT_EVENODD,
#                                            pyclipper.PFT_EVENODD)

#         count[0] += 1

#     Layers[layer]['result'] = union_poly[layer]
#     Layers[layer]['active'] = True


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

    # if union:
    #     for key, layer in Layers.items():
    #         union_wire(Layers, key)

    tools.magenta_print('Wires')    
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

        clip = []
        subj = self.polygon
        for via in vias:
            clip.append(via.polygon)
        
        update = False
        if clip and subj:
            self.polygon = tools.angusj(clip, subj, 'difference')
            if self.polygon:
                self.edgelabels = [None] * len(self.polygon[0])
                update = True


    def update_with_jj_diff(self, jjs):
        """ Find the difference between the wiring
        polygons and the junction base polygons. """

        clip = []
        subj = self.polygon
        for jj in jjs:
            clip.append(jj.polygon)

        if clip and subj:
            self.polygon = tools.angusj(clip, subj, 'difference')
            self.edgelabels = [None] * len(self.polygon)

    def plot_wire(self, cell, gds):
        if self.active:
            for poly in self.polygon:
                cell.add(gdspy.Polygon(poly, gds))
                
                
                
                
                
                
                
                
                
