import pyclipper
import os
import sys
from collections import defaultdict


def number_of_processors():
    """
        Return number of processors on multiple platoforms.
    """

    if os.name == 'nt':
        return int(os.getenv('NUMBER_OF_PROCESSORS'))
    elif sys.platform == 'linux2':
        retv = 0
        with open('/proc/cpuinfo', 'rt') as cpuinfo:
            for line in cpuinfo:
                if line[:9] == 'processor':
                    retv += 1
        return retv
    else:
        raise RuntimeError('unknown platform')


def angusj(clip, subj, clip_type):
    pc = pyclipper.Pyclipper()

    pc.AddPaths(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

    if (clip_type == "difference"):
        subj = pc.Execute(pyclipper.CT_DIFFERENCE,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif (clip_type == "union"):
        subj = pc.Execute(pyclipper.CT_UNION,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)
    elif (clip_type == "intersection"):
        subj = pc.Execute(pyclipper.CT_INTERSECTION,
                          pyclipper.PFT_EVENODD,
                          pyclipper.PFT_EVENODD)

    if (len(subj) > 0):
        return subj
    else:
        return []


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
