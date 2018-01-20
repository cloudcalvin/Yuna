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
        
        tools.print_cellrefs(yuna_cell)
        
        for cell in yuna_cell.get_dependencies(True):
            if cell.name[:3] == 'via':
                labels.vias(cell, self.Layers, self.Atom)
            elif cell.name[:2] == 'jj':
                labels.junctions(cell, self.Layers, self.Atom)
            elif cell.name[:5] == 'ntron':
                labels.ntrons(cell, self.Layers, self.Atom)
               
        self.yuna_flatten = yuna_cell.copy('Yuna Flatten', deep_copy=True)
        self.yuna_flatten.flatten()

    def create_auron_polygons(self):
        """ Union flattened layers and create Auron Cell. 
        Polygons are labels as follow:
        
        1 - vias 
        2 - 
        3 - jjs 
        4 - ntrons 
        5 - ntrons ground 
        6 - ntrons box
        
        Layer with datatype=10 is a hole polygons that will be deleting at meshing.
        """

        polylayers = []
        hole_poly_pair = []
        remove_list = []
        for key, layer in self.Layers.items():
            mtype = ['wire', 'shunt', 'skyplane', 'gndplane']
            if layer['type'] in mtype:
                gds = int(key)
                polygons = self.yuna_flatten.get_polygons(True)

                wires = union.default_layer_polygons(gds, polygons)
                
                ntron_wire = None
                if wires is not None:
                    if (gds, 1) in polygons:
                        wires = union.connect_wire_to_vias(gds, wires, polygons)
                    if (gds, 3) in polygons:
                        wires = union.connect_wire_to_jjs(gds, wires, polygons)
                    if (gds, 4) in polygons:
                        wires = union.connect_wire_to_ntrons(gds, polygons, self.Atom['ntron'], wires)
                        self.auron_cell = union.get_ntron_box(gds, polygons, self.Atom['ntron'], self.auron_cell)
                    if (gds, 5) in polygons:
                        wires = union.connect_wire_to_ntrons_ground(gds, polygons, self.Atom['ntron'], wires)
                        
                        # ntron_wires = polygons[(gds, 5)]
                        # # wires = tools.angusj(ntron_wires, wires, 'difference')
                        # 
                        # self.auron_cell = union.get_ntron_box(gds, polygons, self.Atom['ntron'], self.auron_cell)
                        # device = union.connect_wire_to_ntron_ground(gds, polygons, self.Atom['ntron'], wires)
                        # 
                        # all_sides = union.side_connection(wires, device)
                        # 
                        # # intersected_sides = union.wire_side_intersections(all_sides, wires)
                        # self.auron_cell = union.wire_side_intersections(all_sides, wires, self.auron_cell, device)
                        # 
                        # # if all_sides is not None:
                        # #     for poly in all_sides:
                        # #         self.auron_cell.add(gdsyuna.Polygon(poly, layer=gds, datatype=0))
                        # # if device is not None:
                        # #     for poly in device:
                        # #         self.auron_cell.add(gdsyuna.Polygon(poly, layer=gds, datatype=1))
                        
                    # if wires is not None:
                    #     for i, poly in enumerate(wires):
                    #         if pyclipper.Orientation(poly):
                    #             layerholes.append(poly)
                    #         else:
                    #             holes.append(poly)
                    
                    if wires is not None:
                        for i, poly in enumerate(wires):
                            polylayers.append(i)
                            if not pyclipper.Orientation(poly):
                                hole_poly_pair.append((i-1, i))
                                remove_list.append(i-1)
                                remove_list.append(i)

                    print(list(hole_poly_pair))
                    print(list(set(polylayers) - set(remove_list)))
                        
                    nonhole_poly = list(set(polylayers) - set(remove_list))
                    for i in nonhole_poly:
                        self.auron_cell.add(gdsyuna.Polygon(wires[i], layer=gds, datatype=0))

                    for i, pair in enumerate(hole_poly_pair):
                        self.auron_cell.add(gdsyuna.Polygon(wires[pair[0]], layer=99+gds, datatype=i))
                        self.auron_cell.add(gdsyuna.Polygon(wires[pair[1]], layer=100+gds, datatype=i))
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
            
            
            
            
            
            
            
            
            
            
            
            
            
