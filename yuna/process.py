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
from yuna import structure
from yuna import merge


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


def save_baselayers(auron_cell, basis, my_cell):
    wirepoly = baselayer_list(basis)
    removepoly = holelayer_list(basis)
    for i in list(set(wirepoly) - set(removepoly)):
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[i], layer=basis.gds, datatype=0, verbose=False))

        my_poly = structure.Polygon(basis.baselayer[i], layer=basis.gds, datatype=0, verbose=False)
        my_cell.add(my_poly)


def save_holelayers(auron_cell, basis, my_cell):
    holedata = holelayer_tuple(basis)
    for i, pair in enumerate(holedata):
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[pair[0]], layer=99+basis.gds, datatype=i, verbose=False))
        auron_cell.add(gdsyuna.Polygon(basis.baselayer[pair[1]], layer=100+basis.gds, datatype=i, verbose=False))

        my_poly_1 = structure.Polygon(basis.baselayer[pair[0]], layer=99+basis.gds, datatype=i, verbose=False)
        my_poly_2 = structure.Polygon(basis.baselayer[pair[1]], layer=100+basis.gds, datatype=i, verbose=False)

        my_cell.add(my_poly_1)
        my_cell.add(my_poly_2)


class Junction(object):

    def __init__(self, gds, name, layers, color):
        self.gds = gds
        self.name = name
        self.layers = layers
        self.color = color
        self.position = None
        self.height = None

        self.shunt = {}
        self.ground = {}

    def add_position(self, fabdata):
        """
        The vertical position at which the layer starts.

        Parameters
        ----------
        pos : int
            The position as read from the PCF.
        """

        pos = fabdata['Atoms']['jjs']['pos']

        self.position = float(pos)

    def add_width(self, fabdata):
        """
        The layer width.

        Parameters
        ----------
        width : int
            The width as read from the PCF.
        """

        width = fabdata['Atoms']['jjs']['width']

        self.width = float(width)

    def add_shunt_data(self, fabdata):
        """
        Data that is needed to detect the shunt
        resistance connection in the junction object.
        """

        self.shunt = fabdata['Atoms']['jjs']['shunt']

    def add_ground_data(self, fabdata):
        """
        Data that is needed to detect the ground
        connection in the junction object.
        """

        self.ground = fabdata['Atoms']['jjs']['ground']


class Via(object):

    def __init__(self):
        pass


class Ntron(object):

    def __init__(self):
        pass


class ProcessData(object):

    def __init__(self, name, fabdata):
        self.name = name
        self.fabdata = fabdata
        self.params = None
        self.atoms = None

        self.wires = dict()
        self.vias = dict()
        self.resistors = dict()

        self.components = []


    def add_component(self, component):
        """
        Add an element to the module.

        Parameters
        ----------
        component : object
            The component to be inserted in the module.

        Returns
        -------
        out : ``Module``
            This module.
        """

        self.components.append(component)

        return self

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


def datafield_terminal_labels(cell, datafield):
    for lbl in cell.labels:
        label = structure.Label('1', '2', lbl.text, lbl.position, rotation=lbl.rotation, layer=lbl.layer)
        datafield.add(label)


def detect_components(cell, pdd, datafield):
    """
    Vias are primary components and are detected first.
    JJs and nTrons are defined as secondary components.

    Returns
    -------
    out : gdspy Cell
        The flattened version of original cell with labeled components
    """

    tools.print_cellrefs(cell)

    datafield_terminal_labels(cell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name[:3] == 'via':
            labels.vias(subcell, pdd, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name[:2] == 'jj':
            labels.junctions(subcell, pdd, datafield)

    # for cell in cell_original.get_dependencies(True):
    #     if cell.name[:5] == 'ntron':
    #         labels.ntrons(my_cell, pdd)


def add_terminals(pdd, cell_layout, poly, datafield):
    """
    Parameters
    ----------
    cell_layout : gdspy Cell
        The original layout cell flattened
    cell_wirechain : gdspy Cell
        The cell containing all the layer polygons merged
    """

    key = (pdd.get_term_gds(), 0)

    if key in poly:
        for jj in poly[key]:
            datafield.add(structure.Polygon(jj, *key))


def create_wirechains(pdd, cell, datafield):
    """
    The wirechain for each gdsnumber is created in four phases:

    1. Merge all the normal conducting wires.
    2. Merge the polygons inside each component.
    3. Find the difference between the conducting polygons
       and the component polygons.
    4. Add these polygons to the datafield object.

    Parameters
    ----------
    cell_layout : gdspy Cell
        The original layout cell flattened
    datafield : gdspy Cell
        The cell containing all the layer polygons merged

    Arguments
    ---------
    metals : list
        A list containing the points of the merged polygons.
    components : list
        The merged polygons of the specific layer in the components
        that corresponds to the current datatype value.
    """

    cell_layout = cell.copy('Layout Flatten', deep_copy=True)
    cell_layout.flatten()

    poly = cell_layout.get_polygons(True)

    add_terminals(pdd, cell_layout, poly, datafield)

    for key, layer in pdd.wires.items():
        if key in poly:
            metals = tools.angusj(poly[key], poly[key], 'union')

            for datatype in [1, 3]:
                dkey = (key[0], datatype)
                if dkey in poly:
                    components = tools.angusj(poly[dkey], poly[dkey], 'union')
                    for pp in components:
                        datafield.add(structure.Polygon(pp, *dkey))
                    metals = tools.angusj(components, metals, 'difference')

            for pp in metals:
                datafield.add(structure.Polygon(pp, *key))

    # polygons = cell_layout.get_polygons(True)
    #
    # for key, layer in pdd.wires.items():
    #     basis = connect.BasisLayer(key[0], polygons)
    #     basis.set_baselayer()
    #
    #     if basis.baselayer is not None:
    #         if (basis.gds, 1) in polygons:
    #             basis.connect_to_vias(cell_wirechain, my_cell)
    #         if (basis.gds, 3) in polygons:
    #             basis.connect_to_jjs()
    #         if (basis.gds, 4) in polygons:
    #             nbox = basis.connect_to_ntrons(self.Atom['ntron'], cell_wirechain, my_cell)
    #
    #         save_baselayers(cell_wirechain, basis, my_cell)
    #         save_holelayers(cell_wirechain, basis, my_cell)
    #     else:
    #         pass

# def add_component_labels(celldata, cell_layout, cell_wirechain, my_cell):
#     """ Add labels to Auron Cell. """
#
#     cell_labels = cell_layout.labels
#     vias_config = celldata.atoms['vias'].keys()
#
#     tools.green_print('VIAs defined in the config file:')
#     print(vias_config)
#
#     for lbl in my_cell.get_labels():
#         label = gdsyuna.Label(lbl.text, lbl.position, rotation=lbl.rotation, layer=lbl.layer)
#         cell_wirechain.add(label)
#
#     # lbl = ['P', 'jj', 'ntron', 'sht', 'gnd']
#     # for i, label in enumerate(cell_labels):
#     #
#     #     if label.text in vias_config:
#     #         label.texttype = i
#     #         cell_wirechain.add(label)
#     #
#     #     if label.text.split('_')[0] in lbl:
#     #         label.texttype = i
#     #         cell_wirechain.add(label)
