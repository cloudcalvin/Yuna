from __future__ import print_function # lace this in setup.
from termcolor import colored
from collections import defaultdict


import os
import sys
import json
import gdsyuna
import pyclipper


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


def re_add_cells(flatcell, cell_list):
    for element in cell_list:
        flatcell.add(element)


# def remove_cells(cell):
#     """ This function does a deep copy of the current
#     working cell, without the JJs. It then flattens
#     this cell and afterwards adds the JJs. """
# 
#     print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
#     print('Deep copying cell for Flattening:')
#     print(cell.name)
# 
#     indices = []
#     jj_list = []
#     via_list = []
# 
#     for i, element in enumerate(cell.elements):
#         if isinstance(element, gdsyuna.CellReference):
#             name = element.ref_cell.name
#             if name[:2] == 'JJ':
#                 print(str(i) + ' - Detected JJ: ' + name)
#                 indices.append(i)
#                 jj_list.append(element)
#             if name[:3] == 'via':
#                 print(str(i) + ' - Detected VIA: ' + name)
#                 indices.append(i)
#                 via_list.append(element)
# 
#     for i in sorted(indices, reverse=True):
#         del flatcell.elements[i]


def get_all_cellreferences(yunacell, recursive=False):
    """
    Returns a list of the cells included in this cell as references.

    Parameters
    ----------
    recursive : bool
        If True returns cascading dependencies.

    Returns
    -------
    out : set of ``Cell``
        List of the cells referenced by this cell.
    """
    dependencies = set()
    for element in yunacell.elements:
        if isinstance(element, gdsyuna.CellReference) or isinstance(
                element, gdsyuna.CellArray):
            if recursive:
                dependencies.update(
                    get_all_cellreferences(element.ref_cell, True)
                )
            dependencies.add(element)
    return dependencies


def create_device_cell(device_cellrefs):
    green_print('Create device cells:')
    
    indices = []
    device_list = []
    
    for i, dev in enumerate(device_cellrefs):
        if isinstance(dev, gdsyuna.CellReference):
            name = dev.ref_cell.name
            if name[:2] == 'JJ':
                print(str(i) + ' - Detected JJ: ' + name)
                indices.append(i)
                device_list.append(dev)
            if name[:3] == 'via':
                print(str(i) + ' - Detected VIA: ' + name)
                indices.append(i)
                device_list.append(dev)
        
    device = gdsyuna.Cell('DeviceCells')
    for dev in device_list:
        device.add(dev) 


def flatten_cell(cell):
    """ This function does a deep copy of the current
    working cell, without the JJs. It then flattens
    this cell and afterwards adds the JJs. """

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Deep copying cell for Flattening:')
    print(cell.name)

    indices = []
    device_list = []

    flatcell = cell.copy('flatcell', deep_copy=True)

    for i, mycell in enumerate(flatcell.get_dependencies()):
        name = mycell.name 
        print(name)
        if name[:2] == 'JJ':
            print(str(i) + ' - Detected JJ: ' + name)
            indices.append(i)
            device_list.append(mycell)
        if name[:3] == 'via':
            print(str(i) + ' - Detected VIA: ' + name)
            indices.append(i)
            device_list.append(mycell)
            
        # for i, element in enumerate(mycell.elements):
        #     if isinstance(element, gdsyuna.CellReference):
        #         name = element.ref_cell.name
        #         if name[:2] == 'JJ':
        #             print(str(i) + ' - Detected JJ: ' + name)
        #             indices.append(i)
        #             device_list.append(element)
        #         if name[:3] == 'via':
        #             print(str(i) + ' - Detected VIA: ' + name)
        #             indices.append(i)
        #             device_list.append(element)
            
    device = gdsyuna.Cell('Cells')
    for dev in device_list:
        device.add(dev) 

    for i in sorted(indices, reverse=True):
        del flatcell.elements[i]

    flatcell.flatten()

    # re_add_cells(flatcell, via_list)
    re_add_cells(flatcell, device_list)

    return flatcell

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
#     emergecell = gdsyuna.Cell('emerge')
# 
#     for i, element in enumerate(mycells.elements):
#         if isinstance(element, gdsyuna.CellReference):
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


# Used for detecting is term labels are inside term layers.
# def connect_term_to_wire(terms, wiresets):
#     for term in terms:
#         print(term.labels)
#         wireset = wiresets[term.layer]
#         for wire in wireset.wires:
#             for poly in wire.polygon:
#                 for i in range(len(poly) - 1):
#                     print(i)
#                     x1, y1 = poly[i][0], poly[i][1]
#                     x2, y2 = poly[i+1][0], poly[i+1][1]

#                     cp = midpoint(x1, y1, x2, y2)
#                     term.connect_wire_edge(i, wire, cp)

            
# def create_terminal(Labels, element, terms, mtype):
#     if mtype == 'PolygonSet':
#         for poly in element.polygons:
#             term = layers.Term(poly.tolist())
#             term.connect_label(Labels)
#             terms.append(term)
#     elif mtype == 'Polygon':
#         term = layers.Term(element.points.tolist())
#         term.connect_label(Labels)
#         terms.append(term)



# def get_via_wire_connections(Layers, layer):

#     for w1 in layer['wire1']:
#         wire1 = Layers[w1]['result']

#         for w2 in layer['wire2']:
#             wire2 = Layers[w2]['result']

#             cross = tools.angusj(wire1, wire2, "intersection")

#             viacross = []
#             for subj in cross:
#                 if tools.angusj([subj], layer['result'], "intersection"):
#                     viacross.append(subj)
#             return viacross


# def get_viacross(Layers, Modules, value, subj):
#     """  """

#     clip = get_polygon(Layers, Modules, value['via_layer'])

#     result_list = []
#     viacross = []
#     for poly in subj:
#         if tools.angusj([poly], clip, "intersection"):
#             viacross.append(poly)

#     return viacross
