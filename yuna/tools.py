from __future__ import print_function # lace this in setup.
from termcolor import colored
from collections import defaultdict

import os
import sys
import json
import gdsyuna
import pyclipper
import numpy as np

from yuna import process


def print_cellrefs(cell):
    print('')
    magenta_print('CellReferences')
    for element in cell.elements:
        if isinstance(element, gdsyuna.CellReference):
            print(element)
            print('')


def has_ground(cell, jj_atom):
    key = (int(jj_atom['ground']['gds']), 3)

    if key in cell.get_polygons(True):
        return True
    else:
        return False


def midpoint(x1, y1, x2, y2):
    return ((x1 + x2)/2, (y1 + y2)/2)


def parameter_print(arguments):
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print ('Parameters:')
    for key, value in arguments.items():
        print('      ' + str(key) + ' : ' + str(value))


def red_print(header):
    """ Main program header (Red) """
    print ('\n' + '[' + colored('*', 'red', attrs=['bold']) + '] ', end='')
    print(header)


def magenta_print(header):
    """ Python package header (Purple) """
    print ('\n' + '--- ' + colored(header, 'red', attrs=['bold']) + ' ', end='')
    print ('----------')


def green_print(header):
    """ Function header (Green) """
    print ('\n' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print(header)


def cyan_print(header):
    """ Function header (Green) """
    print ('\n[' + colored('+++', 'cyan', attrs=['bold']) + '] ', end='')
    print(header)


def list_layout_cells(gds):
    """ List the Cells in the GDS layout. """

    gdsii = gdsyuna.GdsLibrary()
    gdsii.read_gds(gds, unit=1.0e-12)

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Cell List:')
    for key, value in gdsii.cell_dict.items():
        print('      -> ' + key)
    print('')


def convert_node_to_3d(wire, z_start):
    layer = np.array(wire).tolist()

    polygons = []
    for pl in layer:
        poly = [[float(y*10e-9) for y in x] for x in pl]
        for row in poly:
            row.append(z_start)
        polygons.append(poly)
    return polygons


def angusj(subj, clip=None, method=None, closed=True):
    """ Angusj clipping library """

    pc = pyclipper.Pyclipper()

    setattr(pc, 'StrictlySimple', True)

    if clip is not None:
        pc.AddPaths(clip, pyclipper.PT_CLIP, True)

    pc.AddPaths(subj, pyclipper.PT_SUBJECT, closed)
    
    subj = None
    if method == 'difference':
        subj = pc.Execute(pyclipper.CT_DIFFERENCE,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif method == 'union':
        subj = pc.Execute(pyclipper.CT_UNION,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    elif method == 'intersection':
        subj = pc.Execute(pyclipper.CT_INTERSECTION,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    elif method == 'exclusive':
        subj = pc.Execute(pyclipper.CT_XOR,
                          pyclipper.PFT_NONZERO,
                          pyclipper.PFT_NONZERO)
    else:
        raise ValueError('please specify a clipping method')

    return subj


def angusj_offset(layer, size):
    """
    Apply polygon offsetting using Angusj.
    Either blow up polygons or blow it down.
    """

    solution = []

    for poly in layer:
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(layer, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

        if size == 'down':
            solution.append(pco.Execute(-10000)[0])
        elif size == 'up':
            solution = pco.Execute(10.0)
        elif size == 'label':
            solution.append(pco.Execute(2000)[0])
        else:
            raise ValueError('please select the Offset function to use')

    return solution


def is_nested_polygons(hole, poly):
    ishole = True
    for point in hole.points:
        if pyclipper.PointInPolygon(point, poly.points) != 1:
            ishole = False
    return ishole
