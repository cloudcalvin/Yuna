from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from collections import defaultdict


import json
import gdspy
import yuna.utils.tools as tools
import pyclipper


def filter_base(baselayer, jjlayer):
    """ If the junction object has more than
    one M0 polygon, then we have to find the
    one with the JJ layer inside it. """

    subj = jjlayer
    clip = baselayer

    baselayer = None
    for poly in clip:
        if does_layers_intersect([poly], subj):
            baselayer = poly

    return baselayer


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


def fill_layers_object(Layers, Elements):
    """
        Add the elements read from GDSPY to the
        corresponding Layers in the JSON object.
    """

    tools.green_print('Elements:')

    for element in Elements:
        if isinstance(element, gdspy.Polygon):
            polygon_result(Layers, element)
        elif isinstance(element, gdspy.PolygonSet):
            polygonset_result(Layers, element)
        elif isinstance(element, gdspy.PolyPath):
            print('Paths not yet supported')
            # layers.path_result(Layers, element)
#         elif isinstance(element, gdspy.CellReference):
#             polygon_jj(Layers, element)


def polygon_result(Layers, element):
    """ Add the polygon to the 'result'
    key in the 'Layers' object """

    print('      Polygons: ', end='')
    print(element)

    for layer, lay_data in Layers.items():
        if lay_data['gds'] == element.layer:
            Layers[layer]['result'].append(element.points.tolist())


def polygonset_result(Layers, element):
    """
    Add the polygons from the PolygonSet to
    the 'result' key in the 'Layers' object.
    """

    print('      PolygonSet: ', end='')
    print(element)

    for layer, lay_data in Layers.items():
        if lay_data['gds'] == element.layers[0]:
            for poly in element.polygons:
                Layers[layer]['result'].append(poly.tolist())


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
