import networkx as nx
import itertools
import json
import gdspy

from yuna import utils

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
        layer = Layer(value)

        if 'position' in value.keys():
            layer.set_position(value['position'])
        if 'width' in value.keys():
            layer.set_width(value['width'])
        if 'metals' in value.keys():
            layer.add_contact_layer(value['metals'])

        if mtype not in ['ix', 'hole', 'res', 'via', 'jj', 'term', 'ntron', 'cap']:
            raise TypeError("mtype `type` is not supported")

        assert isinstance(gds, int)

        self.layers[mtype][gds] = layer


class Layer(object):

    def __init__(self, data):

        self.name = data['name']

        if 'ETL' in data:
            self.etl = data['ETL']
        else:
            self.etl = None

        self.color = data['color']
        self.position = None
        self.width = None
        self.metals = list()

    def set_position(self, num):
        self.position = float(num)

    def set_width(self, num):
        self.width = float(num)

    def add_contact_layer(self, gds):
        if isinstance(gds, list):
            self.metals = gds
        else:
            self.metals.append(gds)
