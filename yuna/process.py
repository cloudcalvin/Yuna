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
        self.Params = config_data['Params']
        self.Layers = config_data['Layers']
        self.Atom = config_data['Atoms']

    def set_gds(self, gds_file):
        self.gdsii = gdsyuna.GdsLibrary()
        self.gdsii.read_gds(gds_file, unit=1.0e-12)

    def create_yuna_flatten(self, cellref):
        yuna_cell = self.gdsii.extract(cellref)
        
        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:3] == 'via':
                tools.green_print('Flattening via: ' + cell.name)
                cell.flatten(single_datatype=1)
                labels.add_to_cell_center(cell)
            elif cell.name[:2] == 'jj':
                tools.green_print('Flattening junction: ' + cell.name)
                cell.flatten(single_datatype=3)

                atom = self.Atom['jjs']

                labels.detect_jj_using_cells(cell, self.Layers)
                labels.label_jj_shunt_connections(cell, atom)
                if labels.has_ground(cell, atom):
                    labels.label_jj_ground_connection(cell, atom)
            elif cell.name[:5] == 'ntron':
                tools.green_print('Flattening ntron: ' + cell.name)
                cell.flatten(single_datatype=4)
                
                atom = self.Atom['ntron']
                
                # label_ntron_connection(cell, atom)
 
        yuna_flatten = yuna_cell.copy('Yuna Flat', deep_copy=True)
        yuna_flatten.flatten()

        return yuna_flatten

    def create_auron_polygons(self, yuna_flatten, auron_cell):
        """ Union flattened layers and create Auron Cell. """

        for key, layer in self.Layers.items():
            mtype = ['wire', 'shunt', 'skyplane', 'gndplane']
            if layer['type'] in mtype:
                wires = union.union_wires(yuna_flatten, auron_cell, int(key), layer['type'])
                wires = union.union_vias(yuna_flatten, auron_cell, int(key), wires)
                wires = union.union_jjs(yuna_flatten, auron_cell, int(key), wires, layer['type'])
                # wires = union.union_ntrons(yuna_flatten, auron_cell, int(key), wires, layer['type'])

                if wires is not None:
                    for poly in wires:
                        auron_cell.add(gdsyuna.Polygon(poly, layer=int(key), datatype=0))
                    
    def add_auron_labels(self, yuna_flatten, auron_cell):
        """ Add labels to Auron Cell. """

        vias_config = self.Atom['vias'].keys()
        tools.green_print('VIAs defined in the config file:')
        print(vias_config)
        
        for i, label in enumerate(yuna_flatten.labels):
            if label.text in vias_config:
                label.texttype = i
                auron_cell.add(label)
                
            if label.text[0] == 'P':
                label.texttype = i 
                auron_cell.add(label)
                
            if label.text[:2] == 'jj':
                label.texttype = i 
                auron_cell.add(label)
                
            if label.text[:5] == 'ntron':
                label.texttype = i 
                auron_cell.add(label)
                
            if label.text == 'gnd_junction':
                label.texttype = i
                auron_cell.add(label)
            elif label.text == 'shunt_junction':
                label.texttype = i
                auron_cell.add(label)
            
    def read_topcell_reference(self):
        topcell = self.gdsii.top_level()[0]
        self.gdsii.extract(topcell)
        self.Labels = self.gdsii.top_level()[0].labels
        self.Elements = self.gdsii.top_level()[0].elements
            
            
            
            
            
            
            
            
            
            
            
            
            
