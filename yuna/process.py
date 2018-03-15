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
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[i], layer=basis.gds, datatype=0, verbose=False))


def save_holelayers(auron_cell, basis):
    holedata = holelayer_tuple(basis)
    for i, pair in enumerate(holedata):
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[pair[0]], layer=99+basis.gds, datatype=i, verbose=False))
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[pair[1]], layer=100+basis.gds, datatype=i, verbose=False))


class ProcessData(object):

    def __init__(self, name, fabdata):
        self.name = name
        self.fabdata = fabdata
        self.params = None
        self.atoms = None

        self.wires = dict()
        self.vias = dict()
        self.resistors = dict()
        self.junctions = dict()

    def add_parameters(self, params):
        self.params = params

    def add_atoms(self, atoms):
        self.atoms = atoms

    def add_layer(self, gds, layerdata):
        self.layers[(gds, 0)] = layerdata

    def get_term_gds(self):
        return int(self.params['TERM']['gds'])

    def add_wires(self):
        for gds, value in self.fabdata['inductive'].items():
            wd = WireData(value['name'], value['color'])

            wd.set_z_start(value['start'])
            wd.set_height(value['height'])

            if 'wire' in value.keys():
                wd.add_contact_layer(value['wire'])

            self.wires[(int(gds), 0)] = wd
        for gds, value in self.fabdata['resistive'].items():
            wd = WireData(value['name'], value['color'])

            wd.set_z_start(value['start'])
            wd.set_height(value['height'])

            if 'wire' in value.keys():
                wd.add_contact_layer(value['wire'])

            self.wires[(int(gds), 0)] = wd

    def add_vias(self):
        for gds, value in self.fabdata['vias'].items():
            wd = ViaData(value['name'], value['color'])

            wd.set_z_start(value['start'])
            wd.set_height(value['height'])

            if 'wire' in value.keys():
                wd.add_contact_layer(value['wire'])

            self.vias[(int(gds), 0)] = wd

    def add_junctions(self):
        for gds, value in self.fabdata['junction'].items():
            wd = JunctionData(value['name'], value['color'])

            wd.set_z_start(value['start'])
            wd.set_height(value['height'])

            if 'wire' in value.keys():
                wd.add_contact_layer(value['wire'])

            self.junctions[(int(gds), 0)] = wd


class WireData(object):

    def __init__(self, name, color):
        self.name = name
        self.z_start = None
        self.height = None
        self.color = color
        self.wires = []

    def set_z_start(self, num):
        self.z_start = float(num)

    def set_height(self, num):
        self.height = float(num)

    def add_contact_layer(self, gds_list):
        self.wires = gds_list


class ViaData(object):

    def __init__(self, name, color):
        self.name = name
        self.z_start = None
        self.height = None
        self.color = color
        self.wires = []

    def set_z_start(self, num):
        self.z_start = float(num)

    def set_height(self, num):
        self.height = float(num)

    def add_contact_layer(self, gds_list):
        self.wires = gds_list


class ResistorData(object):

    def __init__(self, name, color):
        self.name = name
        self.z_start = None
        self.height = None
        self.color = color
        self.wires = []

    def set_z_start(self, num):
        self.z_start = float(num)

    def set_height(self, num):
        self.height = float(num)

    def add_contact_layer(self, gds_list):
        self.wires = gds_list


class JunctionData(object):

    def __init__(self, name, color):
        self.name = name
        self.z_start = None
        self.height = None
        self.color = color
        self.wires = []

    def set_z_start(self, num):
        self.z_start = float(num)

    def set_height(self, num):
        self.height = float(num)

    def add_contact_layer(self, gds_list):
        self.wires = gds_list

# class Config:
#     """
#     Read the data from the GDS file, either from
#     the toplevel CELL of the CELL as speficied
#     the user.
#
#     Attributes
#     ----------
#     Elements : list
#         Elements as read in from the GDS file using the gdsyuna library.
#     Layer : list
#         The Layer object as specified in the json config file.
#
#     Notes
#     -----
#     After the elements has been added to the Layer object,
#     we ably the union polygon operation on the layer polygons.
#     """
#
#     def __init__(self, config_data):
#         self.gdsii = None
#         self.Params = config_data['Params']
#         self.Layers = config_data['Layers']
#         self.Atom = config_data['Atoms']
#
#         self.yuna_labels = None
#         self.yuna_polygons = None
#         self.auron_cell = gdsyuna.Cell('Auron Cell')

# def init_gds_layout(self, gds_file):
#     self.gdsii = gdsyuna.GdsLibrary()
#     self.gdsii.read_gds(gds_file, unit=1.0e-12)

def create_cell_layout(gdsii, cellref, pdd):
    """
    Vias are primary components and are detected first.
    JJs and nTrons are defined as secondary components.

    Returns
    -------
    out : gdspy Cell
        The flattened version of original cell with labeled components
    """

    cell_original = gdsii.extract(cellref)

    tools.print_cellrefs(cell_original)

    for cell in cell_original.get_dependencies(True):
        if cell.name[:3] == 'via':
            labels.vias(cell, pdd)

    for cell in cell_original.get_dependencies(True):
        if cell.name[:2] == 'jj':
            labels.junctions(cell, pdd)

    for cell in cell_original.get_dependencies(True):
        if cell.name[:5] == 'ntron':
            labels.ntrons(cell, pdd)

    cell_layout = cell_original.copy('Yuna Flatten', deep_copy=True)

    return cell_layout.flatten()

    # self.yuna_labels = yuna_flatten.labels
    # self.yuna_polygons = yuna_flatten.get_polygons(True)

def add_terminals(pdd, cell_layout, cell_wirechain):
    """
    Parameters
    ----------
    cell_layout : gdspy Cell
        The original layout cell flattened
    cell_wirechain : gdspy Cell
        The cell containing all the layer polygons merged
    """

    polygons = cell_layout.get_polygons(True)

    gds = pdd.get_term_gds()

    if (gds, 0) in polygons:
        for jj in polygons[(gds, 0)]:
            polygon = gdsyuna.Polygon(jj, layer=gds, datatype=0, verbose=False)
            cell_wirechain.add(polygon)

def create_wirechains(pdd, cell_layout, cell_wirechain):
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

    polygons = cell_layout.get_polygons(True)

    for key, layer in pdd.wires.items():
        # mtype = ['wire', 'shunt', 'skyplane', 'gndplane']
        # if layer.type in mtype:

        basis = connect.BasisLayer(key[0], polygons)
        basis.set_baselayer()

        if basis.baselayer is not None:
            if (basis.gds, 1) in polygons:
                basis.connect_to_vias(cell_wirechain)
            if (basis.gds, 3) in polygons:
                basis.connect_to_jjs()
            if (basis.gds, 4) in polygons:
                nbox = basis.connect_to_ntrons(self.Atom['ntron'], cell_wirechain)

            save_baselayers(cell_wirechain, basis)
            save_holelayers(cell_wirechain, basis)
        else:
            pass

    # for key, layer in pdd.items():
    #     mtype = ['wire', 'shunt', 'skyplane', 'gndplane']
    #     if layer.type in mtype:
    #         basis = connect.BasisLayer(int(key), polygons)
    #         basis.set_baselayer()
    #
    #         if basis.baselayer is not None:
    #             if (basis.gds, 1) in polygons:
    #                 basis.connect_to_vias(cell_wirechain)
    #             if (basis.gds, 3) in polygons:
    #                 basis.connect_to_jjs()
    #             if (basis.gds, 4) in polygons:
    #                 nbox = basis.connect_to_ntrons(self.Atom['ntron'], cell_wirechain)
    #
    #             save_baselayers(cell_wirechain, basis)
    #             save_holelayers(cell_wirechain, basis)
    #         else:
    #             if layer.type == 'shunt':
    #                 if (basis.gds, 3) in polygons:
    #                     for jj in polygons[(gds, 3)]:
    #                         cell_wirechain.add(gdsyuna.Polygon(jj, layer=gds, datatype=0, verbose=False))

def add_component_labels(celldata, cell_layout, cell_wirechain):
    """ Add labels to Auron Cell. """

    cell_labels = cell_layout.labels
    vias_config = celldata.atoms['vias'].keys()

    tools.green_print('VIAs defined in the config file:')
    print(vias_config)

    lbl = ['P', 'jj', 'ntron', 'sht', 'gnd']
    for i, label in enumerate(cell_labels):
        if label.text in vias_config:
            label.texttype = i
            cell_wirechain.add(label)

        if label.text.split('_')[0] in lbl:
            label.texttype = i
            cell_wirechain.add(label)
