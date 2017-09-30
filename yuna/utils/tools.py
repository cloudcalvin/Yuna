import os
import sys

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
    Layers[layer]['active'] = True


def pretty(value, htchar='\t', lfchar='\n', indent=0):
    nlch = lfchar + htchar * (indent + 1)
    if type(value) is dict:
        prettyvalue = pretty(value[key], htchar, lfchar, indent + 1)
        items = [
            nlch + repr(key) + ': ' + prettyvalue
            for key in value
        ]
        return '{%s}' % (','.join(items) + lfchar + htchar * indent)
    elif type(value) is list:
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + lfchar + htchar * indent)
    elif type(value) is tuple:
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + lfchar + htchar * indent)
    else:
        return repr(value)
        
        
        
        
        
        
        
        
        
        
        
        
