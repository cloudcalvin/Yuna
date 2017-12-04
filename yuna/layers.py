from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from collections import defaultdict


import json
import gdspy
import yuna.utils.tools as tools
import pyclipper
from pprint import pprint 


def junction_inside_res(Layers, jj, res_layer):
    """ Filter the res inside the junction
    cell object with a JJ layer inside it. """

    name = get_junction_layer(Layers)
    jj_layer = jj[name]

    if does_layers_intersect([res_layer], jj_layer):
        return True
    else:
        return False


def does_layers_intersect(layer_1, layer_2):
    if tools.angusj(layer_1, layer_2, 'intersection'):
        return True
    else:
        return False


def get_res_layer(Layers):
    layershunt = None
    for key, layer in Layers.items():
        if layer['type'] == 'shunt':
            layershunt = key

    return layershunt


def get_junction_layer(Layers):
    layerjj = None
    for key, layer in Layers.items():
        if layer['type'] == 'junction':
            layerjj = key

    return layerjj


def get_junction_gds(Layers):
    layerjj = None
    for key, layer in Layers.items():
        if layer['type'] == 'junction':
            layerjj = layer['gds']

    return layerjj


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
        self.label = ''
        self.layer = ''
        
    def connect_label(self, Labels):
        for label in Labels:                        
            inside = pyclipper.PointInPolygon(label.position, self.polygon)

            if inside != 0:
                # label.text : "P1 M2 M0"
                self.label = label.text.split()[0]
                self.layer = label.text.split()[1]
                
    def connect_wire_edge(self, i, wire, point):
        """ V1 labeled edge is connected to Via 1.
        P1 is connected to Port 1. """
            
        inside = pyclipper.PointInPolygon(point, self.polygon)

        if inside != 0:
            wire.edgelabels.append(self.label)

# def path_result(Layers, element):
#     """ Add the path to the 'result' key in the 'Layers' object """
#
#     print('      Paths: ', end='')
#     print(element)
#
#     for layer, lay_data in Layers.items():
#         if lay_data['gds'] == element.layer:
#             Layers[layer]['result'].append(element.points.tolist())


# def polygon_jj(Layers, element):
#     """ Add the polygon to the 'jj' key in the 'Layers' object. """
#
#     print('      CellReference: ', end='')
#     print(element)
#
#     name = element.ref_cell.name
#     if name[:2] == 'JJ':
#         tools.green_print('Detecting ' + name)
#         Layers['JJ']['name'].append(name)
#         cellpolygons = gdsii.extract(name).get_polygons(True)
#         transpose_cell(Layers, cellpolygons, element.origin, name)
#
