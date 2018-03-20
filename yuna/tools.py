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


def add_junction_component(fabdata):
    gds = fabdata['Atoms']['jjs']['gds']
    name = fabdata['Atoms']['jjs']['name']
    layers = fabdata['Atoms']['jjs']['layers']
    color = fabdata['Atoms']['jjs']['color']

    jj = process.Junction(gds, name, layers, color)

    jj.add_position(fabdata)
    jj.add_width(fabdata)
    jj.add_shunt_data(fabdata)
    jj.add_ground_data(fabdata)

    return jj


def process_data(fabdata):
    pdd = process.ProcessData('Hypres', fabdata)

    pdd.add_parameters(fabdata['Params'])
    pdd.add_atoms(fabdata['Atoms'])

    pdd.add_wires()
    pdd.add_vias()

    jj = add_junction_component(fabdata)
    pdd.add_component(jj)

    return pdd

def read_config(config_file):
    """ Reads the config file that is written in
    JSON. This file contains the logic of how
    the different layers will interact. """

    data = None
    with open(config_file) as data_file:
        data = json.load(data_file)
    return process_data(data)


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


def is_layer_active(Layers, atom):
    all_layers = True
    for layer in atom['check']:
        if Layers[layer]['active'] == 'False':
            all_layers = False
    return all_layers


def make_active(Layers, layer):
    """
        This function changes the 'active' state of
        the layer in the 'Layers' object in the
        config.json file.
    """

    if layer in Layers:
        Layers[layer]['active'] = True


def convert_node_to_3d(wire, z_start):
    layer = np.array(wire).tolist()

    polygons = []
    for pl in layer:
        poly = [[float(y*10e-9) for y in x] for x in pl]
        for row in poly:
            row.append(z_start)
        polygons.append(poly)
    return polygons


def angusj(clip, subj, method):
    """ Angusj clipping library """

    pc = pyclipper.Pyclipper()

    pc.AddPaths(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

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
    return subj


def angusj_offset(layer, size):
    """
    Apply polygon offsetting using Angusj.
    Either blow up polygons or blow it down.
    """

    solution = []

    for poly in layer:
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(poly, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

        if size == 'down':
            solution.append(pco.Execute(-10000)[0])
            # solution.append(pco.Execute(-1000)[0])
        elif size == 'up':
            solution.append(pco.Execute(10)[0])
        elif size == 'label':
            solution.append(pco.Execute(2000)[0])

    return solution
