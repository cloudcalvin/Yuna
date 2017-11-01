from __future__ import print_function # lace this in setup.
from termcolor import colored

import via
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
    """ * The cells are centered in the middle of the gds
          file canvas. To include this cell into the main
          cell, we have to transpose it to the required position.

        * Save tranposed coordinates in 'Layers' object.
          Maybe we should automate this later by making
          'result' a {} and not a [].
    """

    for key, polygons in cellpolygons.items():
        for layer, lay_data in Layers.items():
            if lay_data['gds'] == key[0]:
                for poly in polygons:
                    for coord in poly:
                        coord[0] = coord[0] + origin[0]
                        coord[1] = coord[1] + origin[1]

                    if (layer == 'JJ'):
                        lay_data['result'].append(poly.tolist())
                    elif (layer == 'JP') or (layer == 'JC'):
                        lay_data['result'].append(poly.tolist())
                    else:
                        lay_data['jj'].append(poly)


def union_polygons(Layers):
    """ Union the normal wiring polygons. """

    tools.green_print('Union Layer:')
    for key, layer in Layers.items():
        if json.loads(layer['union']):
            tools.union_wire(Layers, key, 'result')


class Process:
    """
    Read and parse the JSON config files.
    The main JSON objects are created and updated.

    Parameters
    ----------
    basedir : string
        String that is the main directory of Yuna.
    gds_file : string
        Path to the GDS file in the corresponding test directory.
    config_data : dict
        Full dict as readin and updated from the JSON config file.
    """

    def __init__(self, basedir, gds_file, config_data):
        self.basedir = basedir
        self.gds_file = gds_file
        self.config_data = config_data

    def init_layers(self, cellref):
        """
        Read the data from the GDS file, either from
        the toplevel CELL of the CELL as speficied
        the user.

        Attributes
        ----------
        Elements : list
            Elements as read in from the GDS file using the GDSPY library.
        Layer : list
            The Layer object as specified in the json config file.

        Notes
        -----
        After the elements has been added to the Layer object,
        we ably the union polygon operation on the layer polygons.
        """

        gdsii.read_gds(self.gds_file, unit=1.0e-12)

        Elements = None

        if cellref:
            cell = gdsii.extract(cellref)
            flatcell = tools.flatten_cell(cell)
            Elements = flatcell.elements
        else:
            top_cell = gdsii.top_level()[0]
            gdsii.extract(top_cell)
            Elements = gdsii.top_level()[0].elements

        if Elements:
            Layers = self.config_data['Layers']
            layers.add_elements(Layers, Elements)
            union_polygons(Layers)
        else:
            raise Exception('The Element object cannot be None.')

        return Elements

    def config_layers(self, cellref):
        """ Main loop of the class. Loop over each
        atom, subatom and module. Then update
        the config data structure results. """

        Elements = self.init_layers(cellref)

        Layers = self.config_data['Layers']
        Atom = self.config_data['Atom']

        tools.green_print('Running Atom:')
        for atom in Atom:
            if tools.is_layer_active(Layers, atom):
                self.calculate_atom(atom)

        cParams = params.Params()
        cParams.calculate_area(Elements, Layers)

    def calculate_atom(self, atom):
        """
        * Read the Module data file in
          and save it in the 'Module'
          variable in the Subatom struct.
        * Loop through the modules and calculate
          the result of the Subatom struct.
        """

        print('      Num: ' + atom['id'])

        for subatom in atom['Subatom']:
            tools.read_module(self.basedir, atom, subatom)
            if not json.loads(atom['skip']):
                for module in subatom['Module']:
                    self.calculate_module(atom, subatom, module)

    def connect_layers_with_via(self, value):
        """ Intersect the layers in the 'clip' object
        in the submodule. """

        tools.magenta_print('Connect layers with VIA')

        # subj = self.subject(atom, subatom, module)
        # clip = self.clipper(atom, subatom, module)

        via_object = via.Via(value)

        subj = via_object.subject()
        clip = via_object.clipper()

        # result_list = []
        # if subj and clip:
        #     result_list = tools.angusj(clip, subj, module['method'])
        #     if result_list:
        #         self.update_layer(atom, subatom, module, result_list)
        #     else:
        #         atom['skip'] = 'true'
        # else:
        #     atom['skip'] = 'true'

        # Layers = self.config_data['Layers']
        #
        # poly_1 = module['clip']['layer'][0]
        # poly_2 = module['clip']['layer'][1]
        #
        # print(poly_1.keys()[0])

        # subj = Layers[subj_layer][subj_poly]
        # clip = Layers[clip_layer][clip_poly]
        #
        # result_list = []
        #
        # if subj and clip:
        #     result_list = tools.angusj(clip, subj, 'intersection')
        #     self.my_method(atom, subatom, module, result_list)

    def calculate_module(self, atom, subatom, module):
        """
        * Calculate the Subject polygon list.
        * Calculate the Clippers polygon list.
        * Clip and 1. and 2. using the proposed
          method and save the result.
        """

        for key, value in module.items():
            if key == 'via_connect':
                self.connect_layers_with_via(value)


        # if module['type'] == 'connect':
        #     self.connect_layers_with_via(module)

        # print('          Module: ' + str(module['id']))
        # print('          ' + str(module['desc']))
        # if module['method'] == 'offset':
        #     self.execute_offset(atom, subatom, module)
        # elif module['method'] == 'boolean':
        #     self.execute_bool(atom, subatom, module)
        # elif module['method'] == 'intersection':
        #     self.execute_method(atom, subatom, module)
        # elif module['method'] == 'difference':
        #     self.execute_method(atom, subatom, module)
        # elif module['method'] == 'union':
        #     self.execute_method(atom, subatom, module)
        # else:
        #     raise Exception('Please specify a valid Clippers method')

    def execute_offset(self, atom, subatom, module):
        """ Update the 'result' variable when
        after offsetting the current polygon.
        This method is normally used to detect
        layer overlapping. """

        result_list = []
        subj = self.subject(atom, subatom, module)

        if subj:
            result_list = tools.angusj_offset(subj)
            if result_list:
                self.update_layer(atom, subatom, module, result_list)

    def my_method(self, atom, subatom, module, clip):
        """ Apply polygon method, either union,
        intersection or difference. """

        subj = self.subject(atom, subatom, module)

        result_list = []
        if subj and clip:
            result_list = tools.angusj(clip, subj, module['method'])
            if result_list:
                self.update_layer(atom, subatom, module, result_list)
            else:
                atom['skip'] = 'true'
        else:
            atom['skip'] = 'true'

    def execute_method(self, atom, subatom, module):
        """ Apply polygon method, either union,
        intersection or difference. """

        subj = self.subject(atom, subatom, module)
        clip = self.clipper(atom, subatom, module)

        result_list = []
        if subj and clip:
            result_list = tools.angusj(clip, subj, module['method'])
            if result_list:
                self.update_layer(atom, subatom, module, result_list)
            else:
                atom['skip'] = 'true'
        else:
            atom['skip'] = 'true'

    def execute_bool(self, atom, subatom, module):
        """ We assume that doing a boolean test on
        whether two layers are overlapping, will always
        use the 'intersection' polygon method. """

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

        self.update_layer(atom, subatom, module, inter_list)

    def update_layer(self, atom, subatom, module, result):
        """
            Saves the result back into either:

            1. The Layer struct.
            2. The Subatom struct.
            3. The current Module struct.
        """

        if module['savein'] == 'subatom':
            subatom['result'] = result
        elif module['savein'] == 'module':
            module['result'] = result
#         elif module['savein'] == 'layer':
#             Layers = self.config_data['Layers']
#             layer = module['savein']['layer']
#             poly = module['savein']['poly']
#             Layers[layer][poly] = result
        else:
            raise Exception('Please specify a \'type\' of the sub-module.')

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
        subj_poly = module['subj']['savein']

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
        clip = None

        clip_class = module['clip']['class']
        clip_layer = module['clip']['layer']
        clip_poly = module['clip']['savein']

        if clip_class == 'Layers':
            clip = Layers[clip_layer][clip_poly]
        elif clip_class == 'Atom':
            clip = atom[clip_layer]['result']
        elif clip_class == 'Module':
            modnum = module['clip']['layer']
            clip = module['clip']['result']

        return clip
