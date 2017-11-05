from __future__ import print_function
from collections import defaultdict
from utils import tools


import gdspy
import pyclipper


def remove_poly_with_no_shunt(jjs, subj):
    clip = []
    for jj in jjs:
        clip.append(jj['R2'])

    result_list = []
    no_shunt = []
    for poly in subj:
        result_list = tools.angusj([poly], clip, "intersection")
        if result_list:
            no_shunt.append(poly)

    return no_shunt


def union_wire(Layers, layer):
    count = [0]
    union_poly = defaultdict(list)

    print('wejriuwef')
    print(Layers[layer])
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

    return union_poly[layer]


def get_wire_1(jjs, layer):
    wire_1 = []
    for jj in jjs:
        wire_1.append(jj[layer])

    return wire_1


def get_wire_2(Layers, layer):
    wire_2 = []
    for poly in layer:
        print(poly)
        wire_2.append(poly)

    return wire_2


def get_layercross(subj, clip):
    """ Intersect the layers in the 'clip' object
    in the submodule. """

    layercross = []
    if subj and clip:
        layercross = tools.angusj(clip, subj, 'intersection')
        if not layercross:
            print('Clipping is zero.')

    return layercross


def get_layer_difference(subj, clip):
    """ Intersect the layers in the 'clip' object
    in the submodule. """

    layerdiff = []
    if subj and clip:
        layerdiff = tools.angusj(clip, subj, 'difference')
        if not layerdiff:
            print('Clipping is zero.')

    return layerdiff


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


def copy_module_to_subatom(subatom):
    subatom['result'] = subatom['Module'][-1]['result']


def calculate_jj_json(basedir, gdsii, Layers, Elements, atom):
    tools.magenta_print('Calculating junctions json:')
    jjs = fill_junction_list(gdsii, Layers, Elements)

    for subatom in atom['Subatom']:
        tools.read_module(basedir, atom, subatom)

        for module in subatom['Module']:
            for key, value in module.items():
                if key == 'jj_base':
                    wire_1 = get_wire_1(jjs, value['wire_1']['JJ'])

                    layer = union_wire(Layers, value['wire_2']['Layers'])
                    wire_2 = get_wire_2(Layers, layer)

                    layercross = get_layercross(wire_1, wire_2)
                    module['result'] = layercross
                    print(layercross)
                elif key == 'jj_diff':
                    wire_1 = get_wire_1(jjs, value['wire_1']['JJ'])

                    layer = union_wire(Layers, value['wire_2']['Layers'])
                    wire_2 = get_wire_2(Layers, layer)

                    layerdiff = get_layer_difference(wire_1, wire_2)
#                     module['result'] = layerdiff

                    no_shunt = remove_poly_with_no_shunt(jjs, layerdiff)
                    print(no_shunt)
                    module['result'] = no_shunt

        copy_module_to_subatom(subatom)


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

    def which_junction_layer(self):
        """ Find the junction layer in the process.
        Some fabs like Hypres has multiple JJ layers. """

        cellpolygons = self.gdsii.extract(self.name).get_polygons(True)
        for key, polygons in cellpolygons.items():
            print(key)

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
            for layer, lay_data in self.Layers.items():
                if lay_data['gds'] == key[0]:
                    for poly in polygons:
                        for coord in poly:
                            coord[0] = coord[0] + self.element.origin[0]
                            coord[1] = coord[1] + self.element.origin[1]

                        self.layers[layer] = poly.tolist()

#                         if (layer == 'JJ'):
#                             lay_data['result'].append(poly.tolist())
#                         elif (layer == 'JP') or (layer == 'JC'):
#                             lay_data['result'].append(poly.tolist())
#                         else:
#                             lay_data['jj'].append(poly)
 









