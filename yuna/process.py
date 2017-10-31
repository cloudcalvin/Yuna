from __future__ import print_function # lace this in setup.
from termcolor import colored

import json
import gdspy
import layers
import params
import utils.tools as tools


"""
    Hacker: 1h3d*n
    For: Volundr
    Docs: Algorithm 1
    Date: 31 April 2017

    Description: Using Angusj Clippers library to do
                 polygon manipulations.

    1) The union is done on each polygon of the wiring layer.
    2) The difference and intersection is done with the
    union result and the moat layer.
    3) Note, you might have to multiple each coordinate with
    1000 to convert small floats 0.25 to integers, 250.

    --> union = or
    --> difference = not
    --> intersection = and
"""


gdsii = gdspy.GdsLibrary()


def transpose_cell(Layers, cellpolygons, origin, name):
    """
        The cells are centered in the middle of the gds
        file canvas. To include this cell into the main
        cell, we have to transpose it to the required position.
    """

    for key, polygons in cellpolygons.items():
        for layer, lay_data in Layers.items():
            if lay_data['gds'] == key[0]:
                for poly in polygons:
                    for coord in poly:
                        coord[0] = coord[0] + origin[0]
                        coord[1] = coord[1] + origin[1]

                    # Save tranposed coordinates in 'Layers' object.
                    # Maybe we should automate this later by making
                    # 'result' a {} and not a [].
                    if (layer == 'JJ'):
                        lay_data['result'].append(poly.tolist())
                    elif (layer == 'JP') or (layer == 'JC'):
                        lay_data['result'].append(poly.tolist())
                    else:
                        lay_data['jj'].append(poly)


def union_polygons(Layers):
    """ Union the polygons. """

    tools.green_print('Union Layer:')
    for key, layer in Layers.items():
        if json.loads(layer['union']):
            tools.union_wire(Layers, key, 'result')


# def does_contain_junctions(Elements):
#     """ Check if the layout contains any Junctions. """
#
#     hasjj = False
#     for element in Elements:
#         if isinstance(element, gdspy.CellReference):
#             name = element.ref_cell.name
#             if name[:2] == 'JJ':
#                 hasjj = True
#
#     return hasjj
#
#
# def junction_area(Elements):
#     print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
#     print('Junction areas:')
#     for element in Elements:
#         if isinstance(element, gdspy.CellReference):
#             name = element.ref_cell.name
#             if name[:2] == 'JJ':
#                 for key, value in element.area(True).items():
#                     if key[0] == 6:
#                         print('      ' + name + ' --> ' + str(value * 1e-12) + 'um')
#
#
# def resistance_area(Layers):
#     """
#         * We have to get the center of each resistance polygon.
#         * Test if the center of each polygon is inside
#           layer 9. If so, then remove that polygon.
#         * Finally, we should be left with just the
#           resistance branch polygon.
#     """
#
#     # NB: We have to save the JJ name with the corresponding area value.
#
#     print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
#     print('Parasitic resistance areas:')
#
#     for key, value in Layers.items():
#         if value['type'] == 'resistance':
#             for poly in value['jj']:
#                 poly_element = gdspy.Polygon(poly, 21)
#                 value = poly_element.area(True).values()[0]
#                 print('      ' + key + ' --> ' + str(value * 1e-12) + 'um')



class Process:
    """
        Variables
        ---------
            origin : dict
                This dict contains all the original layers as read in
                from the import GDS file, before manipulation.
            uPoly : dict
                Union of polygon layers, like m1 that has been union, m1 and m2
                that has been intersected, etc.
            iPoly : dict
                Intersection result of two or more polygons.
    """

    def __init__(self, basedir, gds_file, config_data):
        self.basedir = basedir
        self.gds_file = gds_file
        self.config_data = config_data

    def init_layers(self, cellref):
        """
            Fills the 'result' and 'jj' lists inside each
            layer in 'Layers' object.

            Todo
            ----

                * Add PolygonPaths
                * Add nTrons
        """

        gdsii.read_gds(self.gds_file, unit=1.0e-12)

        if cellref:
            cell = gdsii.extract(cellref)
            flatcell = tools.flatten_cell(cell)

            Elements = flatcell.elements
            Layers = self.config_data['Layers']

            layers.add_elements(Layers, Elements)
            union_polygons(Layers)
        else:
            top_cell = gdsii.top_level()[0]
            gdsii.extract(top_cell)

            Elements = gdsii.top_level()[0].elements
            Layers = self.config_data['Layers']

            layers.add_elements(Layers, Elements)
            union_polygons(Layers)

        return Elements

    def config_layers(self, cellref):
        """
            This function is process specific.
            It looks at each layer and dicides
            what to do with it, for example:

            * If it's a wiring layer, union it.
            * If it's a via then test which wiring
              layers is connect and union them.

            Notes
            -----

                * By default all individual layers should
                  be union.

            Todo
            ----

                Implement the default layer union of other
                layers, not just the wiring layers.
        """

        Elements = self.init_layers(cellref)
        Layers = self.config_data['Layers']
        Atom = self.config_data['Atom']

        tools.green_print('Running Atom:')
        for i, atom in enumerate(Atom):
            if tools.is_layer_active(Layers, atom):
                self.calculate_atom(i)

        cParams = params.Params()
        cParams.calculate_area(Elements, Layers)

    def read_module(self, atom_id, subatom_id):
        """  """

        tools.green_print('Reading Module:')

        atom = self.config_data['Atom'][atom_id]
        subatom = atom['Subatom'][subatom_id]

        config_file = self.basedir + '/' + subatom['module'] + '.json'
        print('        Subatom: ' + subatom['module'])

        with open(config_file) as data_file:
            subatom['Module'] = json.load(data_file)['Module']

    def calculate_atom(self, atom_id):
        """
            * Read the Module data file in
              and save it in the 'moduledata'
              variable in the Subatom struct.
            * Loop through the modules and calculate
              the result of the Subatom struct.
        """

        atom = self.config_data['Atom'][atom_id]
        print('      Num: ' + atom['id'])

        for i, subatom in enumerate(atom['Subatom']):
            self.read_module(atom_id, i)
            if not json.loads(atom['skip']):
                for j, module in enumerate(subatom['Module']):
                    self.calculate_module(atom_id, i, j)

    def calculate_module(self, atom_id, subatom_id, module_id):
        """
            1. Calculate the Subject polygon list.
            2. Calculate the Clippers polygon list.
            3. Clip and 1. and 2. using the proposed
               method and save the result.
        """

        atom = self.config_data['Atom'][atom_id]
        subatom = atom['Subatom'][subatom_id]
        module = subatom['Module'][module_id]

        # print(subatom['Module'])

        print('          Module: ' + str(module['id']))
        print('          ' + str(module['desc']))
        if module['method'] == 'offset':
            self.execute_offset(atom_id, subatom_id, module_id)
        elif module['method'] == 'boolean':
            self.execute_bool(atom_id, subatom_id, module_id)
        elif module['method'] == 'intersection':
            self.execute_method(atom_id, subatom_id, module_id)
            print(module)
        elif module['method'] == 'difference':
            self.execute_method(atom_id, subatom_id, module_id)
        elif module['method'] == 'union':
            self.execute_method(atom_id, subatom_id, module_id)
        else:
            raise Exception('Please specify a valid Clippers method')

    def execute_offset(self, atom_id, subatom_id, module_id):
        """ """

        atom = self.config_data['Atom'][atom_id]
        subatom = atom['Subatom'][subatom_id]
        module = subatom['Module'][module_id]

        result_list = []
        subj = self.subject(atom, subatom, module)

        if subj:
            result_list = tools.angusj_offset(subj)
            if result_list:
                self.update_layer(atom_id, subatom_id, module_id, result_list)

    def execute_method(self, atom_id, subatom_id, module_id):
        """ """

        atom = self.config_data['Atom'][atom_id]
        subatom = atom['Subatom'][subatom_id]
        module = subatom['Module'][module_id]

        subj = self.subject(atom, subatom, module)
        clip = self.clipper(atom, subatom, module)

        result_list = []
        if subj and clip:
            result_list = tools.angusj(clip, subj, module['method'])
            if result_list:
                self.update_layer(atom_id, subatom_id, module_id, result_list)
            else:
                atom['skip'] = 'true'
        else:
            atom['skip'] = 'true'

    def execute_bool(self, atom_id, subatom_id, module_id):
        """
            We assume that doing a boolean test on
            whether two layers are overlapping, will always
            use the 'intersection' polygon method.
        """

        atom = self.config_data['Atom'][atom_id]
        subatom = atom['Subatom'][subatom_id]
        module = subatom['Module'][module_id]

        subj = self.subject(atom, subatom, module)
        clip = self.clipper(atom, subatom, module)

        result_list = []
        inter_list = []
        for poly in clip:
            result_list = tools.angusj([poly], subj, "intersection")
            if json.loads(module['delete']):
                if not result_list:
                    inter_list.append(poly)
            else:
                if result_list:
                    inter_list.append(poly)

        self.update_layer(atom_id, subatom_id, module_id, inter_list)

    def update_layer(self, atom_id, subatom_id, module_id, result):
        """
            Saves the result back into either:

            1. The Layer struct.
            2. The Subatom struct.
            3. The current Module struct.
        """

        atom = self.config_data['Atom'][atom_id]
        subatom = atom['Subatom'][subatom_id]
        module = subatom['Module'][module_id]

        # print(result)

        if module['type'] == 'subatom':
            subatom['result'] = result
        elif module['type'] == 'module':
            module['result'] = result
            # module['id'] = '11111123123'
        elif module['type'] == 'layer':
            Layers = self.config_data['Layers']
            layer = module['savein']['layer']
            poly = module['savein']['poly']
            Layers[layer][poly] = result
        else:
            raise Exception('Please specify a \'type\' of the sub-module.')

        print(module['result'])

    def subject(self, atom, subatom, module):
        """
            Parameters
            ----------
                subj_layer : The layer in use.

                subj_class : Can only be "Layers" or "Atom".

                subj_poly : For now it can either be "jj" or "result".

            Atom
            ----

                * Access the last element in the Subatom.
        """

        Atom = self.config_data['Atom']
        Layers = self.config_data['Layers']

        subj_class = module['subj']['class']
        subj_layer = module['subj']['layer']
        subj_poly = module['subj']['poly']

        if subj_class == 'Layers':
            subj = Layers[subj_layer][subj_poly]
        elif subj_class == 'Atom':
            Subatom = Atom[subj_layer]['Subatom'][-1]
            subj = Subatom['result']

        return subj

    def clipper(self, atom, subatom, module):
        """
            Parameters
            ----------

                clip_layer : The layer in use.

                clip_class : Can only be "Layers" or "Atom".

                clip_poly : For now it can either be "jj" or "result".

            Note
            ----

                * Subatom classes must be in Clip Object.
        """

        Layers = self.config_data['Layers']
        Module = subatom['Module']

        clip_class = module['clip']['class']
        clip_layer = module['clip']['layer']
        clip_poly = module['clip']['poly']

        if clip_class == 'Layers':
            clip = Layers[clip_layer][clip_poly]
        elif clip_class == 'Atom':
            clip = atom[clip_layer]['result']
        elif clip_class == 'Module':
            modnum = module['clip']['layer']
            clip = Module[modnum]['result']

        return clip
