from __future__ import print_function # lace this in setup.
from termcolor import colored


import json
import gdspy
import utils.tools as tools


def add_elements(Layers, Elements):
    """
        Add the elements read from GDSPY to the
        corresponding Layers in the JSON object.
    """

    tools.green_print('Elements:')

    for element in Elements:
        if isinstance(element, gdspy.Polygon):
            polygon_result(Layers, element)
        elif isinstance(element, gdspy.PolygonSet):
            polygon_set_result(Layers, element)
        elif isinstance(element, gdspy.PolyPath):
            print('Paths not yet supported')
            # layers.path_result(Layers, element)
        elif isinstance(element, gdspy.CellReference):
            polygon_jj(Layers, element)


def polygon_result(Layers, element):
    """ Add the polygon to the 'result' key in the 'Layers' object """

    print('      Polygons: ', end='')
    print(element)

    for layer, lay_data in Layers.items():
        if lay_data['gds'] == element.layer:
            Layers[layer]['result'].append(element.points.tolist())


def polygon_set_result(Layers, element):
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


def path_result(Layers, element):
    """ Add the path to the 'result' key in the 'Layers' object """

    print('      Paths: ', end='')
    print(element)

    for layer, lay_data in Layers.items():
        if lay_data['gds'] == element.layer:
            Layers[layer]['result'].append(element.points.tolist())


def polygon_jj(Layers, element):
    """ Add the polygon to the 'jj' key in the 'Layers' object. """

    print('      CellReference: ', end='')
    print(element)

    name = element.ref_cell.name
    if name[:2] == 'JJ':
        Layers['JJ']['name'].append(name)
        cellpolygons = gdsii.extract(name).get_polygons(True)
        transpose_cell(Layers, cellpolygons, element.origin, name)






