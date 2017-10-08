from __future__ import print_function # lace this in setup.
from termcolor import colored

import os
import sys
import gdspy

from collections import defaultdict

import pyclipper

def angusj(clip, subj, clip_type):
    """ Angusj clipping library """

    pc = pyclipper.Pyclipper()

    pc.AddPaths(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    if clip_type == "difference":
        subj = pc.Execute(pyclipper.CT_DIFFERENCE,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif clip_type == "union":
        subj = pc.Execute(pyclipper.CT_UNION,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif clip_type == "intersection":
        subj = pc.Execute(pyclipper.CT_INTERSECTION,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)

    if len(subj) > 0:
        return subj
    else:
        return []
        
        
def angusj_offset(subj):
    """ Angusj offset function using Clippers """

    solution = []
    
    for poly in subj:
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(poly, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        solution.append(pco.Execute(-10e4)[0])
        
    return solution


def union_wire(Layers, layer, config_save):
    """
        This function saves the union of each
        individual layer polygon. The result
        is saved in the 'result' variable ien
        the config.json file of the corrisponding
        layer.
    """

    print('      -> ' + layer)

    count = [0]
    union_poly = defaultdict(list)

    cell_layer = Layers[layer][config_save]

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

    Layers[layer][config_save] = union_poly[layer]
    print(union_poly[layer])
    Layers[layer]['active'] = True


def remove_jjs(flatcell, indices):
    for i in sorted(indices, reverse=True):
        del flatcell.elements[i]


def add_jjs_cells(flatcell, jj_list):
    for element in jj_list:
        flatcell.add(element)

        
def flatten_cell(cell):
    """
        This function does a depp copy of the current 
        working cell, with out the JJs. It then flattens
        this cell the afterwards add the JJs.
    """
    
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Deep copying cell:')
    
    indices = []
    jj_list = []
    
    flatcell = cell.copy('flatcell', deep_copy=True)
            
    for i, element in enumerate(flatcell.elements):
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name
            if name == 'aj03_p2j00sb':
                indices.append(i)
                jj_list.append(element)
                    
    remove_jjs(flatcell, indices)
    flatcell.flatten()
    add_jjs_cells(flatcell, jj_list)
    
    return flatcell
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
