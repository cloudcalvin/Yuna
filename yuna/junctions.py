from __future__ import print_function
from collections import defaultdict
from pprint import pprint
from utils import tools


import gdspy
import pyclipper


def get_shunt_layer(Layers):
    layershunt = None
    for key, layer in Layers.items():
        if layer['type'] == 'shunt':
            layershunt = key

    return layershunt


def remove_poly_with_noshunt(Layers, jjs, subj):
    clip = []

    pprint(jjs)

    layershunt = get_shunt_layer(Layers)

    for jj in jjs:
        clip.append(jj[layershunt])

    result_list = []
    no_shunt = []
    for poly in subj:
        result_list = tools.angusj([poly], clip, "intersection")
        if result_list:
            no_shunt.append(poly)

    return no_shunt


def union_wire(Layers, layer):
    count = [0]
    unionlayer = defaultdict(list)
    cell_layer = Layers[layer]['result']

    for poly in cell_layer:
        if (count[0] == 0):
            unionlayer = [poly]
        else:
            clip = poly
            pc = pyclipper.Pyclipper()

            pc.AddPath(clip, pyclipper.PT_CLIP, True)
            pc.AddPaths(unionlayer, pyclipper.PT_SUBJECT, True)

            unionlayer = pc.Execute(pyclipper.CT_UNION,
                                           pyclipper.PFT_EVENODD,
                                           pyclipper.PFT_EVENODD)

        count[0] += 1

    return unionlayer


def union_jj_layers(layers):
    count = [0]
    unionlayer = defaultdict(list)
    print(layers)

#     for poly in layers:
#         clip = poly
#         pc = pyclipper.Pyclipper()
# 
#         pc.AddPath(clip, pyclipper.PT_CLIP, True)
#         pc.AddPaths(unionlayer, pyclipper.PT_SUBJECT, True)
# 
#         unionlayer = pc.Execute(pyclipper.CT_UNION,
#                                        pyclipper.PFT_EVENODD,
#                                        pyclipper.PFT_EVENODD)

#         if (count[0] == 0):
#             unionlayer = [poly]
#         else:
#             clip = poly
#             pc = pyclipper.Pyclipper()
# 
#             pc.AddPath(clip, pyclipper.PT_CLIP, True)
#             pc.AddPaths(unionlayer, pyclipper.PT_SUBJECT, True)
# 
#             unionlayer = pc.Execute(pyclipper.CT_UNION,
#                                            pyclipper.PFT_EVENODD,
#                                            pyclipper.PFT_EVENODD)
# 
#         count[0] += 1

    return unionlayer


def wire_1_list(Layers, jjs, layername):
    wire_1 = []
    for jj in jjs:
        unionlayer = union_jj_layers(jj[layername])
        for poly in unionlayer:
            wire_1.append(poly)
    return wire_1


def wire_2_list(Layers, wirelayer):
    unionlayer = union_wire(Layers, wirelayer)
    wire_2 = []
    for poly in unionlayer:
        wire_2.append(poly)
    return wire_2


def clipping(subj, clip, operation):
    """ Intersect the layers in the 'clip' object
    in the submodule. """

    layercross = []
    if subj and clip:
        if operation == 'intersection':
            layercross = tools.angusj(clip, subj, 'intersection')
        elif operation == 'difference':
            layercross = tools.angusj(clip, subj, 'difference')

        if not layercross:
            print('Clipping is zero.')

    return layercross


def fill_junction_list(gdsii, Layers, Elements):
    """ Loop over all elements, such as
    polygons, polgyonsets, cellrefences, etc
    and find the CellRefences. CellRefs
    which is a junction has to start with JJ. """

    jj_list = []
    for element in Elements:
        if isinstance(element, gdspy.CellReference):
            print('      CellReference: ', end='')
            print(element)

            refname = element.ref_cell.name
            if refname[:2] == 'JJ':
                jj = Junction(gdsii, Layers, element, refname)
                jj.transpose_cell()
                jj_list.append(jj.layers)

    return jj_list


def wires_from_json(Layers, jjs, value):
    jjlayer = value['wire_1']['JJ']
    wirelayer = value['wire_2']['Layers']
    wire_1 = wire_1_list(Layers, jjs, jjlayer)
    wire_2 = wire_2_list(Layers, wirelayer)

    return wire_1, wire_2


def calculate_jj(basedir, gdsii, Layers, Elements, atom):
    tools.magenta_print('Calculating junctions json:')
    jjs = fill_junction_list(gdsii, Layers, Elements)

    for subatom in atom['Subatom']:
        tools.read_module(basedir, atom, subatom)
        for module in subatom['Module']:
            for key, value in module.items():
                if key == 'jj_base':
                    wire_1, wire_2 = wires_from_json(Layers, jjs, value)
                    layercross = clipping(wire_1, wire_2, 'intersection')
                    module['result'] = layercross
                elif key == 'jj_diff':
                    wire_1, wire_2 = wires_from_json(Layers, jjs, value)
                    layerdiff = clipping(wire_1, wire_2, 'difference')
                    module['result'] = layerdiff
#                     respoly = remove_poly_with_noshunt(Layers, jjs, layerdiff)
#                     module['result'] = respoly


class Junction:
    """

    """

    def __init__(self, gdsii, Layers, element, name):
        """  """

        self.gdsii = gdsii
        self.Layers = Layers
        self.element = element
        self.name = name
        self.layers = {}
        self.resistance = None

    def move_jj_coordinates(self, polygons, layername):
        for poly in polygons:
            for coord in poly:
                coord[0] = coord[0] + self.element.origin[0]
                coord[1] = coord[1] + self.element.origin[1]

            self.layers[layername] = poly.tolist()

    def transpose_cell(self):
        """ 
        The cells are centered in the middle of the gds
        file canvas. To include this cell into the main
        cell, we have to transpose it to the required position.

        Save tranposed coordinates in 'Layers' object.
        Maybe we should automate this later by making
        'result' a {} and not a [].
        """

        tools.green_print('Detecting ' + self.name)
        cellpolygons = self.gdsii.extract(self.name).get_polygons(True)

        for key, polygons in cellpolygons.items():
            for layername, layerdata in self.Layers.items():
                if layerdata['gds'] == key[0]:
                    self.move_jj_coordinates(polygons, layername)









