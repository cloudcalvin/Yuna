from __future__ import print_function
from termcolor import colored
from utils import tools
from pprint import pprint


import junctions
import wires
import vias
import json
import gdspy
import layers
import params


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
"""


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
        self.gdsii = gdspy.GdsLibrary()
        self.basedir = basedir
        self.gds_file = gds_file
        self.config_data = config_data
        self.Elements = None
        self.Layers = None
        self.jjs = []

    def user_cellref(self, usercell):
        cell = self.gdsii.extract(usercell)
        flatcell = tools.flatten_cell(cell)
        self.Elements = flatcell.elements

    def toplevel_cellref(self):
        top_cell = gdsii.top_level()[0]
        self.gdsii.extract(top_cell)
        self.Elements = gdsii.top_level()[0].elements

    def init_layers(self, usercell):
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

        self.gdsii.read_gds(self.gds_file, unit=1.0e-12)
        self.Layers = self.config_data['Layers']

        if usercell:
            self.user_cellref(usercell)
        else:
            self.toplevel_cellref()

        layers.fill_layers_object(self.Layers, self.Elements)

    def fill_junction_list(self):
        """ Loop over all elements, such as
        polygons, polgyonsets, cellrefences, etc
        and find the CellRefences. CellRefs
        which is a junction has to start with JJ. """

        Atom = self.config_data['Atom']

        for element in self.Elements:
            if isinstance(element, gdspy.CellReference):
                print('      CellReference: ', end='')
                print(element)

                refname = element.ref_cell.name
                if refname[:2] == 'JJ':
                    jj = junctions.Junction(self.basedir, self.gdsii, self.Layers)

                    layers = junctions.transpose_cell(self.gdsii, self.Layers, refname, element)

                    jj.set_layers(layers)
                    jj.detect_jj(Atom['jj'])

                    self.jjs.append(jj)

    def config_layers(self, cellref):
        """ Main loop of the class. Loop over each
        atom, subatom and module. Then update
        the config data structure results. """

        self.init_layers(cellref)

        Atom = self.config_data['Atom']

        tools.green_print('Running Atom:')
        self.calculate_vias(Atom['vias'])

        self.fill_junction_list()

#         jj = jjs.JunctionObjects(self.basedir, self.gdsii, Layers)
#         jj.calculate_jj(self.Elements, Atom['jj'])

        self.calculate_wires(Atom['wires'], Atom['vias'])

#         cParams = params.Params()
#         cParams.calculate_area(self.Elements, Layers)

    def copy_module_to_subatom(self, subatom):
        subatom['result'] = subatom['Module'][-1]['result']

    def calculate_vias(self, atom):
        """
        * Read the Module data file in
          and save it in the 'Module'
          variable in the Subatom struct.
        * Loop through the modules and calculate
          the result of the Subatom struct.
        """

        print('      Num: ' + str(atom['id']))

        for subatom in atom['Subatom']:
            tools.read_module(self.basedir, atom, subatom)

            for module in subatom['Module']:
                self.calculate_module(atom, subatom, module)

            self.copy_module_to_subatom(subatom)

    def calculate_wires(self, atom, vias):
        """  """

        tools.green_print('Calculating wires json:')

        wire = wires.Wire(self.Layers, atom['Subatom'], vias)
        wire.union_polygons(self.Layers)

        for subatom in atom['Subatom']:
            viadiff = wire.find_via_diff(subatom)
            self.Layers[subatom]['result'] = viadiff

    def calculate_module(self, atom, subatom, module):
        """
        * Calculate the Subject polygon list.
        * Calculate the Clippers polygon list.
        * Clip and 1. and 2. using the proposed
          method and save the result.
        """

        print('          Module: ' + str(module['id']))
        print('          ' + str(module['desc']))

        for key, value in module.items():
            if key == 'via_connect':
                via = vias.Via(self.config_data, subatom)
                layercross = via.get_layercross(value)
                viacross = via.get_viacross(value, layercross)
                module['result'] = viacross
            elif key == 'via_connect_reverse':
                via = vias.Via(self.config_data, subatom)
                layercross = via.get_layercross(value)
                viacross = via.get_viacross(value, layercross)
                wireconnect = via.reverse_via(value, viacross)
                module['result'] = wireconnect
            elif key == 'via_remove':
                via = vias.Via(self.config_data, subatom)
                viacross = via.remove_viacross(value)
                module['result'] = viacross
            
            








