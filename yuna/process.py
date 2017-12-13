from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from pprint import pprint

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

import yuna.junctions as junctions
import yuna.wires as wires
import yuna.vias as vias
import json
import gdspy
import yuna.layers as layers
import yuna.params as params
from yuna.utils import tools
import pyclipper


"""
Hacker: 1h3d*n
For: Volundr
Docs: Algorithm 1
Date: 31 April 2017

Description: Using Angusj Clippers library to do
             polygon manipulations.

1) The union is done on each polygon of the wiring layer.
2) The difference and intersection is done with the
union result and the moat layer.
3) Note, you might have to multiple each coordinate with
1000 to convert small floats 0.25 to integers, 250.
"""

    
def add_label(cell, bb):
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )
    label = gdspy.Label(cell.name, (cx, cy), 'nw', layer=11)
    cell.add(label)


def is_layer_in_layout(wire, polygons):
    return (wire, 0) in polygons


def is_layer_in_via(wire, polygons):
    return (wire, 1) in polygons


def is_layer_in_jj(wire, polygons):
    return (wire, 3) in polygons


def union_vias(vias, wire):
    """ Union vias of the same type. """

    tools.green_print('Union vias:')

    vi = []
    for v1 in vias:
        for v2 in vias:
            if v1 is not v2:
                if layers.does_layers_intersect([v1], [v2]):
                    mvia = tools.angusj([v1], [v2], 'union')
                    for m in mvia:
                        vi.append(m)
    return vi


def union_wires(yuna_cell, auron_cell, wire):
    """  """

    tools.green_print('Union wires:')

    polygons = yuna_cell.get_polygons(True)

    if is_layer_in_layout(wire, polygons):
        wires = yuna_cell.get_polygons(True)[(wire, 0)]
        wires = tools.angusj(wires, wires, 'union')

        # Union vias with wires, but remove redundant 
        # vias that are not connected to any wires.
        if is_layer_in_via(wire, polygons):
            vias = yuna_cell.get_polygons(True)[(wire, 1)]
            for via in vias:
                via_offset = tools.angusj_offset([via], 'up')
                if layers.does_layers_intersect(via_offset, wires):
                    wires = tools.angusj([via], wires, 'union')

        # We know the wires inside a jj, so 
        # we only have to union it with wires
        # and dnt have to remove any jj layers.
        if is_layer_in_jj(wire, polygons):
            jjs = yuna_cell.get_polygons(True)[(wire, 3)]
            for jj in jjs:
                wires = tools.angusj([jj], wires, 'union')

        # Union vias of the same kind, that is not
        # connected to any wires, but shouldn't
        # be deleted. 
        if is_layer_in_via(wire, polygons):
            connected_vias = union_vias(vias, wire)
            for poly in connected_vias:
                auron_cell.add(gdspy.Polygon(poly, layer=wire, datatype=0))

        for poly in wires:
            auron_cell.add(gdspy.Polygon(poly, layer=wire, datatype=0))
            
            
class Config:
    """
    Read the data from the GDS file, either from
    the toplevel CELL of the CELL as speficied
    the user.

    Attributes
    ----------
    Elements : list
        Elements as read in from the GDS file using the GDSPY library.
    Layer : list
        The Layer object as specified in the json config file.

    Notes
    -----
    After the elements has been added to the Layer object,
    we ably the union polygon operation on the layer polygons.
    """
    
    def __init__(self, config_data):
        self.gdsii = None
        self.Params = config_data['Params']
        self.Layers = config_data['Layers']
        self.Atom = config_data['Atoms']

    def set_gds(self, gds_file):
        self.gdsii = gdspy.GdsLibrary()
        self.gdsii.read_gds(gds_file, unit=1.0e-12)
    
    def read_topcell_reference(self):
        topcell = self.gdsii.top_level()[0]
        self.gdsii.extract(topcell)
        self.Labels = self.gdsii.top_level()[0].labels
        self.Elements = self.gdsii.top_level()[0].elements
        
    def read_usercell_reference(self, cellref, auron_cell):
        yuna_cell = self.gdsii.extract(cellref)

        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:3] == 'via':
                cell.flatten(single_datatype=1)

                bb = cell.get_bounding_box()
                add_label(cell, bb)
            elif cell.name[:2] == 'jj':
                cell.flatten(single_datatype=3)
                
                for key, layer in self.Layers.items():
                    if layer['type'] == 'junction':                
                        for element in cell.elements:
                            bb = element.get_bounding_box()
                            if isinstance(element, gdspy.PolygonSet):
                                if element.layers == [int(key)]:
                                    add_label(cell, bb)
                            elif isinstance(element, gdspy.Polygon):
                                if element.layers == int(key):
                                    add_label(cell, bb)

        yuna_flatten = yuna_cell.copy('yuna_flatten', deep_copy=True)
        yuna_flatten.flatten()
        
        for key, layer in self.Layers.items():
            if layer['type'] == 'wire' or layer['type'] == 'shunt':
                union_wires(yuna_flatten, auron_cell, int(key))

        for label in yuna_flatten.labels:
            auron_cell.add(label)








