from __future__ import print_function
from __future__ import absolute_import

from termcolor import colored
from pprint import pprint

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

import yuna.junctions as junctions
import yuna.wires as wires
import yuna.vias as vias
import json
import gdspy
import yuna.layers as layers
import yuna.params as params
from yuna.utils import tools


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


def shrink_touching_layers(layer):
    return tools.angusj_offset(layer, 'down')


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
        self.wireset_list = []
        self.jjs = []
        self.vias = []

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

    def is_jj_cell(self, element):
        """  """

        jjbool = False
        if isinstance(element, gdspy.CellReference):
            print('      CellReference: ', end='')
            print(element)
            refname = element.ref_cell.name
            if refname[:2] == 'JJ':
                jjbool = True

        return jjbool

    def add_via(self, via):
        self.vias.append(via)

    def add_jj(self, jj):
        self.jjs.append(jj)

    def add_to_wireset_list(self, wireset):
        self.wireset_list.append(wireset)

    def config_layers(self, cellref, union):
        """ Main loop of the class. Loop over each
        atom, subatom and module. Then update
        the config data structure results. """

        self.init_layers(cellref)

        Atom = self.config_data['Atom']

        tools.green_print('Running Atom:')

        self.calculate_vias(Atom['vias'])
        self.fill_via_list(Atom['vias'])
        self.fill_jj_list(Atom['jj'])
        self.fill_wires_list(union)

        # Find the differene between the via, jjs and wires.
        for wireset in self.wireset_list:
            for wire in wireset.wires:
                wire.update_with_via_diff(self.vias)
                wire.update_with_jj_diff(self.jjs)

        # Connect the wires and via objects.
        for via in self.vias:
            for wireset in self.wireset_list:
                for wire in wireset.wires:
                    via.connect_wires(wire)

        # cParams = params.Params()
        # cParams.calculate_area(self.Elements, Layers)

    def fill_wires_list(self, union):
        """ Loop through the Layer object
        and save each layer as a wire object."""

        tools.green_print('Calculating wires json:')

        if union:
            wires.union_polygons(self.Layers)
        else:
            print('Note: UNION wires is not set')

        for name, layers in self.Layers.items():
            if (layers['type'] == 'wire') or (layers['type'] == 'resistance') or (layers['type'] == 'shunt'):
                wireset = wires.WireSet(name, layers['gds'])

                for layer in layers['result']:
                    view = json.loads(layers['view'])

                    offset = shrink_touching_layers([layer])

                    wire = wires.Wire(offset, active=view)
                    wireset.add_wire_object(wire)

                self.add_to_wireset_list(wireset)

    def copy_module_to_subatom(self, subatom):
        subatom['result'] = subatom['Module'][-1]['result']

    def calculate_vias(self, atom):
        """ * Read the Module data file in
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

    def fill_via_list(self, atom):
        """ Copy the 'result' list in the vias
        Subatom to the self.vias list of
        via objects. """

        _id = 0
        for subatom in atom['Subatom']:
            for poly in subatom['result']:
                via = vias.Via(_id)

                via.set_base(poly)
                via.set_gds(subatom['gds'])

                self.add_via(via)
                _id += 1

    def fill_jj_list(self, atom):
        """ Loop over all elements, such as
        polygons, polgyonsets, cellrefences, etc
        and find the CellRefences. CellRefs
        which is a junction has to start with JJ. """

        for element in self.Elements:
            if self.is_jj_cell(element):
                gdsii = self.gdsii
                Layers = self.Layers

                layers = junctions.transpose_cell(gdsii, Layers, element)

                jj = junctions.Junction(self.basedir, self.Layers)

                jj.set_layers(layers)
                jj.detect_jj(atom)

                self.add_jj(jj)

    def calculate_module(self, atom, subatom, module):
        """
        * Calculate the Subject polygon list.
        * Calculate the Clippers polygon list.
        * Clip and 1. and 2. using the proposed
          method and save the result.
        """

        print('          Module: ' + str(module['id']))
        print('          ' + str(module['desc']))

        for key, value in list(module.items()):
            if key == 'via_connect':
                layercross = vias.get_layercross(self.Layers, subatom['Module'], value)
                viacross = vias.get_viacross(self.Layers, subatom['Module'], value, layercross)
                module['result'] = viacross
            elif key == 'via_connect_reverse':
                layercross = vias.get_layercross(self.Layers, subatom['Module'], value)
                viacross = vias.get_viacross(self.Layers, subatom['Module'], value, layercross)
                wireconnect = vias.reverse_via(self.Layers, subatom['Module'], value, viacross)
                module['result'] = wireconnect
            elif key == 'via_remove':
                viacross = vias.remove_viacross(self.Layers, subatom['Module'], value)
                module['result'] = viacross
