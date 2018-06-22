import os
import sys
import json
import gdspy
import pyclipper
import numpy as np
import logging

from yuna import process
from collections import defaultdict


um = 10e-6
nm = 10e-9
pm = 10e-12

unit = 1e-6
grid = 5e-9

datatype = {'path': 0,
            'via': 1,
            'jj': 3,
            'ntron': 7}

llabels = {}


def calculate_ports(label, raw_pdk_data):
    from collections import namedtuple

    assert len(label) == 3 or len(label) == 2

    plates = {}

    Plates = namedtuple('Plates', ['term', 'label'])

    gds1 = string_to_gds(label[1], raw_pdk_data)
    plates[gds1] = Plates(term='+', label=label[1])

    if len(label) == 3:
        gds2 = string_to_gds(label[2], raw_pdk_data)
        plates[gds2] = Plates(term='+', label=label[2])

    return plates


def string_to_gds(name, raw_pdk_data, ltype=['ix']):
    for lt in ltype:
        for data in raw_pdk_data['Layers'][lt]:
            if data['name'] == name:
                if 'ETL' in data:
                    return data['ETL']
                else:
                    return data['layer']
    return None


def print_cellrefs(cell):
    print('')
    magenta_print('CellReferences')
    for element in cell.elements:
        if isinstance(element, gdspy.CellReference):
            print(element)
            print('')


def midpoint(x1, y1, x2, y2):
    return ((x1 + x2)/2, (y1 + y2)/2)


def parameter_print(arguments):
    print ('Parameters:')
    for key, value in arguments.items():
        print('      ' + str(key) + ' : ' + str(value))


def red_print(header):
    """ Main program header (Red) """
    print(header)


def magenta_print(header):
    """ Python package header (Purple) """
    print ('----------')
    print('')


def end_print():
    print ('\n--------------------------')


def green_print(header):
    """ Function header (Green) """
    print(header)


def cyan_print(header):
    """ Function header (Green) """
    print(header)


def list_layout_cells(gds):
    """ List the Cells in the GDS layout. """

    gdsii = gdspy.GdsLibrary()
    gdsii.read_gds(gds, unit=1.0e-12)

    print('Cell List:')
    for key in gdsii.cell_dict.keys():
        print('      -> ' + key)
    print('')


def convert_node_to_3d(wire, position):
    layer = np.array(wire).tolist()

    polygons = []
    for pl in layer:
        poly = [[float(y*10e-9) for y in x] for x in pl]
        for row in poly:
            row.append(position)
        polygons.append(poly)
    return polygons


def write_cell(key, name, terminals):
    cell = gdspy.Cell(name)

    for name, term in terminals.items():
        poly = gdspy.Polygon(term.edge, *key)
        cell.add(poly)


def angusj_path(subj, clip):
    pc = pyclipper.Pyclipper()

    pc.AddPath(subj, pyclipper.PT_SUBJECT, False)
    pc.AddPath(clip, pyclipper.PT_CLIP, True)

    solution = pc.Execute2(pyclipper.CT_INTERSECTION,
                           pyclipper.PFT_NONZERO,
                           pyclipper.PFT_NONZERO)

    path = pyclipper.PolyTreeToPaths(solution)

    #TODO: Add check here.

    return path




def is_nested_polygons(hole, poly):
    for point in hole.points:
        if pyclipper.PointInPolygon(point, poly.points) != 1:
            return False
    return True
