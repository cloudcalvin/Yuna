import numpy as np
import networkx as nx
import itertools
import json
import gdsyuna
import pyclipper
import labels
import union

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from yuna import tools


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
                    
                    
class Config:
    """
    Read the data from the GDS file, either from
    the toplevel CELL of the CELL as speficied
    the user.

    Attributes
    ----------
    Elements : list
        Elements as read in from the GDS file using the gdsyuna library.
    Layer : list
        The Layer object as specified in the json config file.

    Notes
    -----
    After the elements has been added to the Layer object,
    we ably the union polygon operation on the layer polygons.
    """
    
    def __init__(self, config_data):
        self.gdsii = None
        self.Layers = config_data['Layers']
        self.Atom = config_data['Atoms']

        self.yuna_flatten = None
        self.auron_cell = gdsyuna.Cell('Auron Cell')

    def init_gds_layout(self, gds_file):
        self.gdsii = gdsyuna.GdsLibrary()
        self.gdsii.read_gds(gds_file, unit=1.0e-12)

    def create_yuna_flatten(self, cellref):
        yuna_cell = self.gdsii.extract(cellref)
        
        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:3] == 'via':
                tools.green_print('Flattening via: ' + cell.name)
                cell.flatten(single_datatype=1)

                labels.add_label(cell, cell, cell.name)
            elif cell.name[:2] == 'jj':
                tools.green_print('Flattening junction: ' + cell.name)
                cell.flatten(single_datatype=3)

                labels.get_jj_layer(cell, self.Layers)
                labels.get_shunt_connections(cell, self.Atom['jjs'])

                if tools.has_ground(cell, self.Atom['jjs']):
                    labels.get_ground_connection(cell, self.Atom['jjs'])
            elif cell.name[:5] == 'ntron':
                tools.green_print('Flattening ntron: ' + cell.name)
                cell.flatten(single_datatype=4)

                for element in cell.elements:
                    if isinstance(element, gdsyuna.PolygonSet):
                        if element.layers[0] == 45:
                            element.polygons = tools.angusj(element.polygons, element.polygons, 'union')
               
                # cell = labels.get_ntron_layer(cell, self.Atom['ntron'])
                # print(cell.elements)
 
        self.yuna_flatten = yuna_cell.copy('Yuna Flatten', deep_copy=True)
        self.yuna_flatten.flatten()

    def create_auron_polygons(self):
        """ Union flattened layers and create Auron Cell. """

        for key, layer in self.Layers.items():
            mtype = ['wire', 'shunt', 'skyplane', 'gndplane']
            if layer['type'] in mtype:
                gds = int(key)
                polygons = self.yuna_flatten.get_polygons(True)

                wires = union.default_layer_polygons(gds, polygons)
                
                if wires is not None:
                    if (gds, 1) in polygons:
                        wires = union.connect_wire_to_vias(gds, wires, polygons)
                    if (gds, 3) in polygons:
                        wires = union.connect_wire_to_jjs(gds, wires, polygons)
                    if (gds, 4) in polygons:
                        self.auron_cell = union.connect_wire_to_ntrons(gds, polygons, self.Atom['ntron'], self.auron_cell)
                            
                    for poly in wires:
                        self.auron_cell.add(gdsyuna.Polygon(poly, layer=gds, datatype=0))
                else:
                    if mtype == 'shunt':
                        if (gds, 3) in polygons:
                            for jj in polygons[(gds, 3)]:
                                self.auron_cell.add(gdsyuna.Polygon(jj, layer=gds, datatype=0))
                    
    def add_auron_labels(self):
        """ Add labels to Auron Cell. """

        vias_config = self.Atom['vias'].keys()
        tools.green_print('VIAs defined in the config file:')
        print(vias_config)
        
        for i, label in enumerate(self.yuna_flatten.labels):
            if label.text in vias_config:
                label.texttype = i
                self.auron_cell.add(label)
                
            if label.text[0] == 'P':
                label.texttype = i 
                self.auron_cell.add(label)
                
            if label.text[:2] == 'jj':
                label.texttype = i 
                self.auron_cell.add(label)
                
            if label.text[:5] == 'ntron':
                label.texttype = i 
                self.auron_cell.add(label)
                
            if label.text == 'gnd_junction':
                label.texttype = i
                self.auron_cell.add(label)
            elif label.text == 'shunt_junction':
                label.texttype = i
                self.auron_cell.add(label)
            
            
            
            
            
            
            
            
            
            
            
            
            
