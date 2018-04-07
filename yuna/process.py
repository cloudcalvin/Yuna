import networkx as nx
import itertools
import json
import gdsyuna

from yuna import utils
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
        wd = Layer(value['name'], mtype)

        if 'position' in value.keys():
            wd.set_position(value['position'])
        if 'width' in value.keys():
            wd.set_width(value['width'])
        if 'wire' in value.keys():
            wd.add_contact_layer(value['wire'])

        if mtype not in ['ix', 'hole', 'res', 'via', 'jj', 'term', 'ntron']:
            raise TypeError("mtype `type` is not supported")

        assert isinstance(gds, int)

        self.layers[mtype][gds] = wd


class Layer(object):

    def __init__(self, name, mtype):
        self.name = name
        self.type = mtype
        self.position = None
        self.width = None
        self.wires = []

    def set_position(self, num):
        self.position = float(num)

    def set_width(self, num):
        self.width = float(num)

    def add_contact_layer(self, gds_list):
        self.wires = gds_list
