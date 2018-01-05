from __future__ import print_function # lace this in setup.
from termcolor import colored
from collections import defaultdict


import os
import sys
import json
import gdsyuna
import pyclipper


def does_layers_intersect(layer_1, layer_2):
    if angusj(layer_1, layer_2, 'intersection'):
        return True
    else:
        return False


def midpoint(x1, y1, x2, y2):
    return ((x1 + x2)/2, (y1 + y2)/2)


def remove_cells(yunacell):
    indices = []
    for i, element in enumerate(yunacell.elements):
        if isinstance(element, gdsyuna.CellReference):
            name = element.ref_cell.name
            if name == 'aj_res_bar_gds':
                print(i)
                indices.append(i)

    for i in sorted(indices, reverse=True):
        del yunacell.elements[i]


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

    gdsii = gdsyuna.GdsLibrary()
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
    # pc.StrictlySimple(True)

    pc.AddPaths(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    subj = None
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
            solution.append(pco.Execute(-1000000)[0])
            # solution.append(pco.Execute(-10)[0])
        elif size == 'up':
            solution.append(pco.Execute(10)[0])
        elif size == 'label':
            solution.append(pco.Execute(2000)[0])

    return solution


# def re_add_cells(flatcell, cell_list):
#     for element in cell_list:
#         flatcell.add(element)


# def get_all_cellreferences(yunacell, recursive=False):
#     """
#     Returns a list of the cells included in this cell as references.

#     Parameters
#     ----------
#     recursive : bool
#         If True returns cascading dependencies.

#     Returns
#     -------
#     out : set of ``Cell``
#         List of the cells referenced by this cell.
#     """
#     dependencies = set()
#     for element in yunacell.elements:
#         if isinstance(element, gdsyuna.CellReference) or isinstance(
#                 element, gdsyuna.CellArray):
#             if recursive:
#                 dependencies.update(
#                     get_all_cellreferences(element.ref_cell, True)
#                 )
#             dependencies.add(element)
#     return dependencies


# def create_device_cell(device_cellrefs):
#     green_print('Create device cells:')
    
#     indices = []
#     device_list = []
    
#     for i, dev in enumerate(device_cellrefs):
#         if isinstance(dev, gdsyuna.CellReference):
#             name = dev.ref_cell.name
#             if name[:2] == 'JJ':
#                 print(str(i) + ' - Detected JJ: ' + name)
#                 indices.append(i)
#                 device_list.append(dev)
#             if name[:3] == 'via':
#                 print(str(i) + ' - Detected VIA: ' + name)
#                 indices.append(i)
#                 device_list.append(dev)
        
#     device = gdsyuna.Cell('DeviceCells')
#     for dev in device_list:
#         device.add(dev) 


# def flatten_cell(cell):
#     """ This function does a deep copy of the current
#     working cell, without the JJs. It then flattens
#     this cell and afterwards adds the JJs. """

#     print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
#     print('Deep copying cell for Flattening:')
#     print(cell.name)

#     indices = []
#     device_list = []

#     flatcell = cell.copy('flatcell', deep_copy=True)

#     for i, mycell in enumerate(flatcell.get_dependencies()):
#         name = mycell.name 
#         print(name)
#         if name[:2] == 'JJ':
#             print(str(i) + ' - Detected JJ: ' + name)
#             indices.append(i)
#             device_list.append(mycell)
#         if name[:3] == 'via':
#             print(str(i) + ' - Detected VIA: ' + name)
#             indices.append(i)
#             device_list.append(mycell)
            
#     device = gdsyuna.Cell('Cells')
#     for dev in device_list:
#         device.add(dev) 

#     for i in sorted(indices, reverse=True):
#         del flatcell.elements[i]

#     flatcell.flatten()

#     re_add_cells(flatcell, device_list)

#     return flatcell

# def read_module(basedir, atom, subatom):
#     """ Read the Module json file and save
#     it in the Subatom 'Module' variable. """

#     green_print('Reading Module:')
#     config_file = basedir + '/' + subatom['module'] + '.json'
#     print('        Subatom: ' + subatom['module'])
#     with open(config_file) as data_file:
#         subatom['Module'] = json.load(data_file)['Module']