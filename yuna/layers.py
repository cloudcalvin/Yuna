from __future__ import print_function
from termcolor import colored


import json
import gdspy
import utils.tools as tools


def does_layers_intersect(layer_1, layer_2):
    if tools.angusj(layer_1, layer_2, 'intersection'):
        return True
    else:
        return False


def get_shunt_layer(Layers):
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





