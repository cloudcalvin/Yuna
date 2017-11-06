from __future__ import print_function
from collections import defaultdict
from pprint import pprint
from utils import tools


import gdspy
import layers
import pyclipper


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


def jj_inside_res(Layers, jj, res_layer):
    """ Filter the res inside the junction
    cell object with a JJ layer inside it. """

    name = layers.get_junction_layer(Layers)
    jj_layer = jj[name]

    if layers.does_layers_intersect(jj_layer, res_layer):
        return True
    else:
        return False


def filter_juntion_resistance(Layers, jjs):
    """ Filter the resistance polygons that
    has the JJ layer inside them. Look at the
    Japan junction layouts. """

    shuntname = layers.get_shunt_layer(Layers)

    jj_res = []
    for jj in jjs:
        layer_res = jj[shuntname]

        for res in layer_res:
            print(res)
            if not jj_inside_res(Layers, jj, [res]):
                jj_res.append(res)

    return jj_res


def union_res(Layers, res_layer):
    count = [0]
    unionlayer = defaultdict(list)

    for poly in res_layer:
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

def remove_poly_with_noshunt(Layers, jjs, subj):
#     shuntname = layers.get_shunt_layer(Layers)

#     clip = []
#     for jj in jjs:
#         layershunt = jj[shuntname]
#         print(layershunt)
#         clip.append(layershunt)

    res_layer = filter_juntion_resistance(Layers, jjs)
    clip = union_res(Layers, res_layer)
    print(clip)

    shuntedlayer = []
    for poly in subj:
        print(subj)
        if layers.does_layers_intersect([poly], clip):
            shuntedlayer.append(poly)

    return shuntedlayer


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


def jj_base_layer(Layers, subj, clip):
    """ 
    If the junction object has more
    than one M0 polygon, then we have to
    find the one with the JJ layer inside it.
    """

    baselayer = None
    for poly in clip:
        if layers.does_layers_intersect([poly], subj):
            baselayer = poly

    return baselayer


def prepare_wire_1(Layers, jjs, layername):
    """ Get the M0 polygon in the Junction
    objects that has a JJ layer inside them. """

    wire_1 = []
    for jj in jjs:
        name = layers.get_junction_layer(Layers)
        M0 = jj[layername]
        JJ = jj[name]

        jjM0 = jj_base_layer(Layers, JJ, M0)
        wire_1.append(jjM0)

    return wire_1


def prepare_wire_2(Layers, wirelayer):
    """ Get a list of the wires that 
    connect the junctions to other
    circuit elements. These polygons
    have to be union. """

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


def wires_from_json(Layers, jjs, value):
    """
    The 'JJ' key means that we have to
    access the corresponding layer from
    the Junction Object List.
    """

    M0layer = value['wire_1']['JJ']
    M2layer = value['wire_2']['Layers']

    wire_1 = prepare_wire_1(Layers, jjs, M0layer)
    wire_2 = prepare_wire_2(Layers, M2layer)

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
#                     module['result'] = layerdiff
                    respoly = remove_poly_with_noshunt(Layers, jjs, layerdiff)
                    module['result'] = respoly


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

    def save_transposed_coords(self, polygons, layername):
        """ Transpose each layer in the Junction reference
        and save it by layername in a dict. """

        poly_list = []
        for poly in polygons:
            for coord in poly:
                coord[0] = coord[0] + self.element.origin[0]
                coord[1] = coord[1] + self.element.origin[1]

            poly_list.append(poly.tolist())

        self.layers[layername] = poly_list

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
                    self.save_transposed_coords(polygons, layername)












