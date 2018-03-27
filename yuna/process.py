import networkx as nx
import itertools
import json
import gdsyuna

from yuna import tools
from yuna import labels

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import collections as cl


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


class ProcessConfigData(object):

    def __init__(self):
        self.params = None
        self.atoms = None

        self.layers = cl.defaultdict(dict)
        self.components = []

    def add_parameters(self, params):
        self.params = params

    def add_atoms(self, atoms):
        self.atoms = atoms

    def add_layer(self, mtype, gds, value):
        wd = Layer(value['name'])

        if 'position' in value.keys():
            wd.set_z_start(value['position'])
        if 'width' in value.keys():
            wd.set_height(value['width'])
        if 'wire' in value.keys():
            wd.add_contact_layer(value['wire'])

        if mtype not in ['ix', 'res', 'via', 'jj', 'term', 'ntron']:
            raise TypeError("mtype `type` is not supported")

        assert isinstance(gds, int)

        self.layers[mtype][gds] = wd

    # def add_component(self, component):
    #     """
    #     Add an element to the module.
    #
    #     Parameters
    #     ----------
    #     component : object
    #         The component to be inserted in the module.
    #
    #     Returns
    #     -------
    #     out : ``Module``
    #         This module.
    #     """
    #
    #     self.components.append(component)
    #
    #     return self

    # def add_wires(self):
    #     for gds, value in self.fabdata['ix'].items():
    #         wd = WireData(value['name'], value['color'])
    #
    #         wd.set_z_start(value['position'])
    #         wd.set_height(value['width'])
    #
    #         if 'wire' in value.keys():
    #             wd.add_contact_layer(value['wire'])
    #
    #         self.wires[(int(gds), 0)] = wd
    #     for gds, value in self.fabdata['res'].items():
    #         wd = WireData(value['name'], value['color'])
    #
    #         wd.set_z_start(value['position'])
    #         wd.set_height(value['width'])
    #
    #         if 'wire' in value.keys():
    #             wd.add_contact_layer(value['wire'])
    #
    #         self.wires[(int(gds), 0)] = wd
    #
    # def add_vias(self):
    #     for gds, value in self.fabdata['via'].items():
    #         wd = ViaData(value['name'], value['color'])
    #
    #         wd.set_z_start(value['position'])
    #         wd.set_height(value['width'])
    #
    #         if 'wire' in value.keys():
    #             wd.add_contact_layer(value['wire'])
    #
    #         self.vias[(int(gds), 0)] = wd


class Layer(object):

    def __init__(self, name):
        self.name = name
        self.z_start = None
        self.height = None
        self.wires = []

    def set_z_start(self, num):
        self.z_start = float(num)

    def set_height(self, num):
        self.height = float(num)

    def add_contact_layer(self, gds_list):
        self.wires = gds_list


class Via(object):

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


class Ntron(object):

    def __init__(self):
        pass
