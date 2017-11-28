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


def shrink_touching_layers(layer):
    return tools.angusj_offset(layer, 'down')


def midpoint(x1, y1, x2, y2):
    return ((x1 + x2)/2, (y1 + y2)/2)
            

def connect_term_to_wire(terms, wiresets):
    print('wenfnwieufbewe')
    for term in terms:
        print(term.labels)
        wireset = wiresets[term.layer]
        for wire in wireset.wires:
            for poly in wire.polygon:
                for i in range(len(poly) - 1):
                    print(i)
                    x1, y1 = poly[i][0], poly[i][1]
                    x2, y2 = poly[i+1][0], poly[i+1][1]

                    cp = midpoint(x1, y1, x2, y2)
                    term.connect_wire_edge(i, wire, cp)

        # TODO: Add verbose parameter
        # for wire in wireset.wires:
        #     for edge in wire.edgelabels:
        #         print(edge)
            
            
def create_terminal(Labels, element, terms):
    poly = element.points.tolist()
    term = layers.Term(poly)
    term.connect_label(Labels)
    terms.append(term)
            
            
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
        self.Params = config_data['Params']
        self.Layers = config_data['Layers']
        self.Atom = config_data['Atoms']

        self.Elements = None
        self.Terms = []
        self.Labels = None
        self.gdsii = None
        
    def set_gds(self, gds_file):
        self.gdsii = gdspy.GdsLibrary()
        self.gdsii.read_gds(gds_file, unit=1.0e-12)
        
    def read_topcell_reference(self):
        topcell = self.gdsii.top_level()[0]
        self.gdsii.extract(topcell)
        self.Labels = self.gdsii.top_level()[0].labels
        self.Elements = self.gdsii.top_level()[0].elements
        
    def read_usercell_reference(self, cellref):
        cell = self.gdsii.extract(cellref)
        flatcell = tools.flatten_cell(cell)
        self.Labels = flatcell.labels                
        self.Elements = flatcell.elements
        
    def parse_gdspy_elements(self):
        """ Add the elements read from GDSPY to the
        corresponding Layers in the JSON object. """

        tools.green_print('Elements:')
        for element in self.Elements:
            if isinstance(element, gdspy.Polygon):            
                if element.layer == self.Params['TERM']['gds']:
                    create_terminal(self.Labels, element, self.Terms)
                else:
                    self.from_polygon_object(element)
            elif isinstance(element, gdspy.PolygonSet):
                self.from_polygonset_object(element)   
                
    def from_polygon_object(self, element):
        """ Add the polygon to the 'result'
        key in the 'Layers' object """

        print(element)
        for layer, lay_data in self.Layers.items():
            if lay_data['gds'] == element.layer:
                self.Layers[layer]['result'].append(element.points.tolist())

    def from_polygonset_object(self, element):
        """ Add the polygons from the PolygonSet to
        the 'result' key in the 'Layers' object. """

        print(element)
        for layer, lay_data in self.Layers.items():
            if lay_data['gds'] == element.layers[0]:
                for poly in element.polygons:
                    self.Layers[layer]['result'].append(poly.tolist())


class Process:
    """
    Read and parse the JSON config files.
    The main JSON objects are created and updated.

    Parameterss
    ----------
    basedir : string
        String that is the main directory of Yuna.
    gds_file : string
        Path to the GDS file in the corresponding test directory.
    config_data : dict
        Full dict as readin and updated from the JSON config file.
    """

    def __init__(self, basedir, config):
        self.basedir = basedir
        self.config = config
        
        self.wiresets = {}
        self.terms = []
        self.vias = []
        self.jjs = []

    def circuit_layout(self, union):
        """ Main loop of the class. Loop over each
        atom, subatom and module. Then update
        the config data structure results. """

        tools.green_print('Running Atom:')

        if self.config.Atom['vias']:
            self.calculate_vias(self.config.Atom['vias'])
        if self.config.Atom['jjs']:
            junctions.fill_jj_list(self.config, self.basedir, self.jjs)
        
        wires.fill_wiresets(self.config.Layers, self.wiresets, union)
        connect_term_to_wire(self.config.Terms, self.wiresets)

        # Find the differene between the via, jjs and wires.
        for key, wireset in self.wiresets.items():
            for wire in wireset.wires:
                if self.config.Atom['vias']:
                    wire.update_with_via_diff(self.vias)
                if self.config.Atom['jjs']:
                    wire.update_with_jj_diff(self.jjs)

        # # Connect the wires with via objects.
        # if self.config.Atom['vias']:
        #     for via in self.vias:
        #         for key, wireset in self.wiresets.items():
        #             tools.green_print(key)
        #             for wire in wireset.wires:
        #                 via.connect_wires(wire)
        #     
        # # Connect the wires with jj objects.            
        # if self.config.Atom['jjs']:
        #     for jj in self.jjs:
        #         for key, wireset in self.wiresets.items():
        #             for wire in wireset.wires:
        #                 jj.connect_wires(wire)
            
        # cParams = params.Params()
        # cParams.calculate_area(self.Elements, Layers)

    def update_wire_offset(self):
        for name, wireset in self.wiresets.items():
            for wires in wireset.wires:
                wires.polygon = shrink_touching_layers(wires.polygon)        
        
    def calculate_vias(self, atom):
        """ 
        * Read the Module data file in
          and save it in the 'Module'
          variable in the Subatom struct.
        * Loop through the modules and calculate
          the result of the Subatom struct.
        """

        print('      Num: ' + str(atom['id']))

        for subatom in atom['Subatom']:
            tools.read_module(self.basedir, atom, subatom)
            
            for module in subatom['Module']:
                self.calculate_module(atom, subatom, module)
                
            subatom['result'] = subatom['Module'][-1]['result']

        vias.fill_via_list(self.vias, atom)

    def calculate_module(self, atom, subatom, module):
        """
        * Calculate the Subject polygon list.
        * Calculate the Clippers polygon list.
        * Clip and 1. and 2. using the proposed
          method and save the result.
        """

        print('          Module: ' + str(module['id']))
        print('          ' + str(module['desc']))

        for key, value in list(module.items()):
            if key == 'via_connect':
                layercross = vias.get_layercross(self.config.Layers, subatom['Module'], value)
                viacross = vias.get_viacross(self.config.Layers, subatom['Module'], value, layercross)
                module['result'] = viacross
            elif key == 'via_connect_reverse':
                layercross = vias.get_layercross(self.config.Layers, subatom['Module'], value)
                viacross = vias.get_viacross(self.config.Layers, subatom['Module'], value, layercross)
                wireconnect = vias.reverse_via(self.config.Layers, subatom['Module'], value, viacross)
                module['result'] = wireconnect
            elif key == 'via_remove':
                viacross = vias.remove_viacross(self.config.Layers, subatom['Module'], value)
                module['result'] = viacross
