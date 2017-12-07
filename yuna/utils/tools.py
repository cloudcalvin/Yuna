from __future__ import print_function # lace this in setup.
from termcolor import colored
from collections import defaultdict


import os
import sys
import json
import gdspy
import pyclipper


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
    print ('\n' + '[' + colored('*', 'magenta', attrs=['bold']) + '] ', end='')
    print ('--- ' + header + ' ----------')


def green_print(header):
    """ Function header (Green) """
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print(header)


def cyan_print(header):
    """ Function header (Green) """
    print ('\n[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print(header)


def list_layout_cells(gds):
    """ List the Cells in the GDS layout. """

    gdsii = gdspy.GdsLibrary()
    gdsii.read_gds(gds, unit=1.0e-12)

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Cell List:')
    for key, value in gdsii.cell_dict.items():
        print('      -> ' + key)


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


def angusj(clip, subj, method):
    """ Angusj clipping library """

    pc = pyclipper.Pyclipper()

    pc.AddPaths(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    if method == 'difference':
        subj = pc.Execute(pyclipper.CT_DIFFERENCE,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif method == 'union':
        subj = pc.Execute(pyclipper.CT_UNION,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif method == 'intersection':
        subj = pc.Execute(pyclipper.CT_INTERSECTION,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)

    if len(subj) > 0:
        return subj
    else:
        return []


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
            solution.append(pco.Execute(-1000000)[0])
        elif size == 'up':
            solution.append(pco.Execute(10)[0])
        elif size == 'label':
            solution.append(pco.Execute(2000)[0])

    return solution


def union_wire(Layers, layer):
    """ This function saves the union of each
    individual layer polygon. The result
    is saved in the 'result' variable
    in the config.json file of the
    corrisponding layer. """

    print('      -> ' + layer)

    count = [0]
    union_poly = defaultdict(list)

    cell_layer = Layers[layer]['result']

    for poly in cell_layer:
        if (count[0] == 0):
            union_poly[layer] = [poly]
        else:
            clip = poly
            pc = pyclipper.Pyclipper()

            pc.AddPath(clip, pyclipper.PT_CLIP, True)
            pc.AddPaths(union_poly[layer], pyclipper.PT_SUBJECT, True)

            union_poly[layer] = pc.Execute(pyclipper.CT_UNION,
                                           pyclipper.PFT_EVENODD,
                                           pyclipper.PFT_EVENODD)

        count[0] += 1

    Layers[layer]['result'] = union_poly[layer]
    Layers[layer]['active'] = True


def re_add_cells(flatcell, cell_list):
    for element in cell_list:
        flatcell.add(element)


def remove_cells(cell):
    """ This function does a deep copy of the current
    working cell, without the JJs. It then flattens
    this cell and afterwards adds the JJs. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Deep copying cell for Flattening:')
    print(cell.name)

    indices = []
    jj_list = []
    via_list = []

    for i, element in enumerate(cell.elements):
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name
            if name[:2] == 'JJ':
                print(str(i) + ' - Detected JJ: ' + name)
                indices.append(i)
                jj_list.append(element)
            if name[:3] == 'via':
                print(str(i) + ' - Detected VIA: ' + name)
                indices.append(i)
                via_list.append(element)

    for i in sorted(indices, reverse=True):
        del flatcell.elements[i]


def flatten_cell(cell):
    """ This function does a deep copy of the current
    working cell, without the JJs. It then flattens
    this cell and afterwards adds the JJs. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Deep copying cell for Flattening:')
    print(cell.name)

    indices = []
    jj_list = []
    via_list = []

    flatcell = cell.copy('flatcell', deep_copy=True)

    for i, element in enumerate(flatcell.elements):
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name
            if name[:2] == 'JJ':
                print(str(i) + ' - Detected JJ: ' + name)
                indices.append(i)
                jj_list.append(element)
            if name[:3] == 'via':
                print(str(i) + ' - Detected VIA: ' + name)
                indices.append(i)
                via_list.append(element)

    for i in sorted(indices, reverse=True):
        del flatcell.elements[i]

    flatcell.flatten()

    re_add_cells(flatcell, via_list)
    re_add_cells(flatcell, jj_list)

    return cell

def read_module(basedir, atom, subatom):
    """ Read the Module json file and save
    it in the Subatom 'Module' variable. """

    green_print('Reading Module:')
    config_file = basedir + '/' + subatom['module'] + '.json'
    print('        Subatom: ' + subatom['module'])
    with open(config_file) as data_file:
        subatom['Module'] = json.load(data_file)['Module']


# def my_cell_edits(cell, Layers, Atom):
#     """ This function does a deep copy of the current
#     working cell, without the JJs. It then flattens
#     this cell and afterwards adds the JJs. """
# 
#     print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
#     print('Deep copying mycell for Flattening:')
# 
#     indices = []
#     jj_list = []
#     via_list = []
# 
#     atom = Atom['jjs']
# 
#     mycells = cell.copy('mycells', deep_copy=True)
#     emergecell = gdspy.Cell('emerge')
# 
#     for i, element in enumerate(mycells.elements):
#         if isinstance(element, gdspy.CellReference):
#             name = element.ref_cell.name
#             if name[:2] == 'JJ':
#                 print(str(i) + ' - Detected JJ: ' + name)
#                 indices.append(i)
#                 jj_list.append(element)
# 
#                 cellpolygons = element.ref_cell.get_polygons(True)
# 
#                 jj_cell = element.ref_cell.flatten()
#                 for key, poly in cellpolygons.items():
#                     if key == (21, 0):
# #                         print(poly)
#                         for p in poly:
#                             jj_cell.remove_polygon_by_layer(key[0], p)
#                         
# #     print(mycells.elements)
# #     mycells.remove(indices)
# #     print('\nAfter')
# #     print(mycells.elements)
# 
#     mycells.flatten()
# 
#     # readd_cells(flatcell, via_list)
#     # readd_cells(flatcell, jj_list)








