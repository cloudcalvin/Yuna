from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from collections import defaultdict


import json
import gdspy
import yuna.utils.tools as tools
import pyclipper
from pprint import pprint 


def does_layers_intersect(layer_1, layer_2):
    if tools.angusj(layer_1, layer_2, 'intersection'):
        return True
    else:
        return False


def get_res_layer(Layers):
    name = None
    for key, layer in Layers.items():
        if layer['type'] == 'shunt':
            name = key
    return name


def get_junction_layer(Layers):
    name = None
    for key, layer in Layers.items():
        if layer['type'] == 'junction':
            name = key
    return name


def get_junction_gds(Layers):
    num = None
    for key, layer in Layers.items():
        if layer['type'] == 'junction':
            num = layer['gds']
    return num


def union_wires(Layers, layer):
    count = [0]
    unionlayer = defaultdict(list)
    cell_layer = Layers[layer]['result']

    for poly in cell_layer:
        if (count[0] == 0):
            unionlayer = [poly]
        else:
            clip = poly
            pc = pyclipper.Pyclipper()

            pc.AddPath(clip, pyclipper.PT_CLIP, True)
            pc.AddPaths(unionlayer, pyclipper.PT_SUBJECT, True)

            unionlayer = pc.Execute(pyclipper.CT_UNION,
                                           pyclipper.PFT_EVENODD,
                                           pyclipper.PFT_EVENODD)
        count[0] += 1
    return unionlayer


class Term:
    def __init__(self, polygon):
        """
        Parameters
        ----------
        Polygon : list
            List of points that defines the polygon
            of the terminal layer.
        Label : string
            The unique TEXT string name. This Labels
            the polygon for later use in the meshing.
        Layer : string
            The layer that the terminal is connected to.
        """

        self.polygon = polygon
        self.label_pos = None
        self.label = ''
        self.layer = ''

    def connect_label(self, Labels):
        for label in Labels:
            print(label.position)
            inside = pyclipper.PointInPolygon(label.position, self.polygon)
            if inside != 0:
                """ label.text : "P1 M2 M0" """
                self.label = label.text.split()[0]
                self.layer = label.text.split()[1]
                self.label_pos = label.position
                
    def connect_wire_edge(self, i, wire, point):
        """ V1 labeled edge is connected to Via 1.
        P1 is connected to Port 1. """
            
        inside = pyclipper.PointInPolygon(point, self.polygon)
        if inside != 0:
            wire.edgelabels.append(self.label)









