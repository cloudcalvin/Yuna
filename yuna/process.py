from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from pprint import pprint

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import itertools
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


def is_layer_in_layout(wire, polygons):
    return (wire, 0) in polygons


def is_layer_in_via(wire, polygons):
    return (wire, 1) in polygons


def is_layer_in_jj(wire, polygons):
    return (wire, 3) in polygons


def add_label(cell, name, bb):
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 1.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )
    label = gdspy.Label(name, (cx, cy), 'nw', layer=11)
    cell.add(label)


def union_vias(vias, wire):
    """ Union vias of the same type. """

    tools.green_print('Union vias:')

    via_union = list()
    for v1 in vias:
        for v2 in vias:
            if v1 is not v2:
                if layers.does_layers_intersect([v1], [v2]):
                    for union in tools.angusj([v1], [v2], 'union'):
                        via_union.append(union)

    return list(via_union for via_union,_ in itertools.groupby(via_union))


def union_wires(yuna_cell, auron_cell, wire):
    """  """

    # tools.green_print('Union wires:')

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

            # Union vias of the same kind, that is not
            # connected to any wires, but shouldn't
            # be deleted. 
            connected_vias = union_vias(vias, wire)
            for poly in connected_vias:
                auron_cell.add(gdspy.Polygon(poly, layer=wire, datatype=0))

        # We know the wires inside a jj, so 
        # we only have to union it with wires
        # and dnt have to remove any jj layers.
        if is_layer_in_jj(wire, polygons):
            jjs = yuna_cell.get_polygons(True)[(wire, 3)]
            for jj in jjs:
                wires = tools.angusj([jj], wires, 'union')

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

    def intersect_via_shunt(self, via_res, via, polygons, key, jj):
        if key[0] == jj['shunt']:
            if layers.does_layers_intersect([via], polygons):
                for poly in tools.angusj([via], polygons, 'intersection'):
                    via_res.append(poly)

    def intersect_via_wire(self, via_wire, via, polygons, key, jj):
        if key[0] == jj['wire']:
            if layers.does_layers_intersect([via], polygons):
                for poly in tools.angusj([via], polygons, 'intersection'):
                    via_wire.append(via)

    def intersect_wire_ground(self, via_gnd, via, polygons, key, jj):
        if key[0] == jj['ground']:
            if layers.does_layers_intersect([via], polygons):
                for poly in tools.angusj([via], polygons, 'intersection'):
                    via_gnd.append(via)
                        
    def to_canvas_center(self, cell):
        """
        The cells are centered in the middle of the gds
        file canvas. To include this cell into the main
        cell, we have to transpose it to the required position.

        Save tranposed coordinates in 'Layers' object.
        Maybe we should automate this later by making
        'result' a {} and not a [].
        """

        layers = dict()
        for key, polygons in cell.get_polygons(True).items():
            print(key, polygons)
            origin = [0.0, 0.0]
            for poly in polygons:
                for coord in poly:
                    coord[0] = origin[0] - coord[0]
                    coord[1] = origin[1] - coord[1]
        #     for layername, layerdata in Layers.items():
        #         if layerdata['gds'] == key[0]:
        #             layers[layername] = save_coords(polygons, element)
        # return layers


    # def save_coords(polygons, element):
    #     """ Transpose each layer in the Junction reference
    #     and save it by layername in a dict. """
    # 
    #     poly_list = []
    #     for poly in polygons:
    #         for coord in poly:
    #             coord[0] = coord[0] + element.origin[0]
    #             coord[1] = coord[1] + element.origin[1]
    #         poly_list.append(poly.tolist())
    #     return poly_lis

    def detect_via_using_cells(self, cell):
        bb = cell.get_bounding_box()
        add_label(cell, cell.name, bb)

    def detect_jj_using_cells(self, cell):
        for key, layer in self.Layers.items():
            if layer['type'] == 'junction':                
                for element in cell.elements:
                    bb = element.get_bounding_box()
                    if isinstance(element, gdspy.PolygonSet):
                        if element.layers == [int(key)]:
                            add_label(cell, cell.name, bb)
                    elif isinstance(element, gdspy.Polygon):
                        if element.layers == int(key):
                            add_label(cell, cell.name, bb)

    def detect_shunt_connections(self, cell):
        """ Add via labels for the shunt 
        resistance inside the jj cell. """

        jj = self.Atom['jjs']['shunt']
        jjlayers = [jj['wire'], jj['shunt'], jj['via']]

        jj_cell = gdspy.Cell('jj_cell')

        via_poly = None
        for key, polygons in cell.get_polygons(True).items():
            if key[0] == jj['via']:
                via_poly = polygons

        # Check of ons hierdie 3 stappe kan morf.
        via_res = []
        for via in via_poly:
            for key, polygons in cell.get_polygons(True).items():
                self.intersect_via_shunt(via_res, via, polygons, key, jj)

        via_wire = []
        for via in via_res:
            for key, polygons in cell.get_polygons(True).items():
                self.intersect_via_wire(via_wire, via, polygons, key, jj)

        via_gnd = []
        for i, via in enumerate(via_wire):
            for key, polygons in cell.get_polygons(True).items():
                self.intersect_wire_ground(via_gnd, via, polygons, key, jj)

        # Add the labels to the center of these via polygons
        for via in via_wire:
            poly = gdspy.Polygon(via, jj['via'])
            bb = poly.get_bounding_box()

            # TODO: Check wat ek hier doen! Engiunious!!!!!!
            add_label(cell, jj['name'], bb)
            jj_cell.add(poly)

        for via in via_gnd:
            poly = gdspy.Polygon(via, jj['via'])
            bb = poly.get_bounding_box()

            # TODO: CHeck wat ek hier doen! Engiunious!!!!!!
            add_label(cell, jj['name'] + '_gnd', bb)
            jj_cell.add(poly)

        # for key, polygons in cell.get_polygons(True).items():
        #     if key[0] in jjlayers:
        #         for poly in polygons:
        #             jj_cell.add(gdspy.Polygon(poly, key[0]))

    def read_usercell_reference(self, cellref, auron_cell):
        yuna_cell = self.gdsii.extract(cellref)
        
        for cell in yuna_cell.get_dependencies(True):
            dx, dy = cell.to_canvas_center()
            
            if cell.name[:3] == 'via':
                cell.flatten(single_datatype=1)
                self.detect_via_using_cells(cell)
            elif cell.name[:2] == 'jj':
                cell.flatten(single_datatype=3)
                self.detect_jj_using_cells(cell)
                self.detect_shunt_connections(cell)
 
        yuna_flatten = yuna_cell.copy('yuna_flatten', deep_copy=True)
        yuna_flatten.flatten()
        
        for key, layer in self.Layers.items():
            if layer['type'] == 'wire' or layer['type'] == 'shunt':
                union_wires(yuna_flatten, auron_cell, int(key))

        for i, label in enumerate(yuna_flatten.labels):
            label.texttype = i
            auron_cell.add(label)








