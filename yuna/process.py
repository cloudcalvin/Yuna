import numpy as np
import networkx as nx
import itertools
import json
import gdsyuna
import pyclipper
from yuna import labels
from yuna import connect

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


def holelayer_tuple(basis):
    holedata = []
    for i, poly in enumerate(basis.baselayer):
        if not pyclipper.Orientation(poly):
            holedata.append((i-1, i))
    return holedata
    
    
def holelayer_list(basis):
    removepoly = []
    for i, poly in enumerate(basis.baselayer):
        if not pyclipper.Orientation(poly):
            removepoly.append(i-1)
            removepoly.append(i)
    return removepoly

    
def baselayer_list(basis):
    wirepoly = []
    for i, poly in enumerate(basis.baselayer):
        wirepoly.append(i)
    return wirepoly
    

def save_baselayers(auron_cell, basis):
    wirepoly = baselayer_list(basis)
    removepoly = holelayer_list(basis)
    for i in list(set(wirepoly) - set(removepoly)):
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[i], layer=basis.gds, datatype=0))


def save_holelayers(auron_cell, basis):
    holedata = holelayer_tuple(basis)
    for i, pair in enumerate(holedata):
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[pair[0]], layer=99+basis.gds, datatype=i))
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[pair[1]], layer=100+basis.gds, datatype=i))
            
                    
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

        self.yuna_labels = None
        self.yuna_polygons = None
        self.auron_cell = gdsyuna.Cell('Auron Cell')

    def init_gds_layout(self, gds_file):
        self.gdsii = gdsyuna.GdsLibrary()
        self.gdsii.read_gds(gds_file, unit=1.0e-12)

    def create_yuna_flatten(self, cellref):
        """  """
    
        yuna_cell = self.gdsii.extract(cellref)
        
        tools.print_cellrefs(yuna_cell)
        
        # First get all the VIAs
        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:3] == 'via':
                labels.vias(cell, self.Layers, self.Atom)

        # Second get all the JJs 
        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:2] == 'jj':
                labels.junctions(cell, self.Layers, self.Atom)

        # Third get all the NTRONs
        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:5] == 'ntron':
                labels.ntrons(cell, self.Layers, self.Atom)

        yuna_flatten = yuna_cell.copy('Yuna Flatten', deep_copy=True)
        yuna_flatten.flatten()

        self.yuna_labels = yuna_flatten.labels
        self.yuna_polygons = yuna_flatten.get_polygons(True)

    def create_auron_polygons(self):
        """ 
            Union flattened layers and create Auron Cell. 
            Polygons are labels as follow:
            
            1 - vias
            2 - 
            3 - jjs
            4 - ntrons
            5 - ntrons ground
            6 - ntrons box

            Variables
            ---------

            wirepoly : list
                Normal interconnected wire polygons in the top-level cell.
            holepoly : tuple
                Holds the indexes of the polygon with a hole and the hole itself.
            removelist : list
                Is the difference between wirepoly and holepoly. Indexes that has to be removed.
            
            Layer with datatype=10 is a hole polygons that will be deleting at meshing.
        """

        for key, layer in self.Layers.items():
            mtype = ['wire', 'shunt', 'skyplane', 'gndplane']
            if layer['type'] in mtype:
                
                basis = connect.BasisLayer(int(key), self.yuna_polygons)
                
                basis.set_baselayer()
                
                if basis.baselayer is not None:
                    if (basis.gds, 1) in self.yuna_polygons:
                        basis.connect_to_vias(self.auron_cell)
                    if (basis.gds, 3) in self.yuna_polygons:
                        basis.connect_to_jjs()
                    if (basis.gds, 4) in self.yuna_polygons:
                        nbox = basis.connect_to_ntrons(self.Atom['ntron'], self.auron_cell)

                    save_baselayers(self.auron_cell, basis)
                    save_holelayers(self.auron_cell, basis)
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
        
        lbl = ['P', 'jj', 'ntron', 'gnd_junction', 'shunt_junction']
        for i, label in enumerate(self.yuna_labels):
            if label.text in vias_config:
                label.texttype = i
                self.auron_cell.add(label)

            # if label.text.split('_')[0] in lbl:
            #     label.texttype = i
            #     self.auron_cell.add(label)

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
            
            
            
            
            
            
            
            
            
            
            
            
            
