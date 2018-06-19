import gdspy
import pprint
import yuna
import numpy as np
import os
import sys
import json
import collections as cl

from yuna import process
from yuna import utils

from yuna.utils import nm
from yuna.utils import logging
from yuna.utils import datatype

import yuna.labels as labels
from yuna.masternode import *


logger = logging.getLogger(__name__)


class Geometry(object):
    """
    Contains all geometric information of the circuit layout.
    The gds file are parsed and linked with the PDK.

    name : string
        The name of the Cell extracted.
    original_labels : list
        List of the labels added by the user in the gds file.
    original_terms : list
        List containing the polygons of the terminal layers
        added by the user in the gds file.
    labels : list
        All the labels that was detected and created. These
        include the device detection labels and that manually
        set by the user.
    masks : dict
        Contains the gdsnumber as the key with a list of all
        the mMsk objects of that specific layer type.
    polygons : [gds][datatype]
        The polygons of Mask objects presented in a dictionary
        format.
    """

    def __init__(self, cell, pcf):
        self.name = cell.name

        self.raw_pdk_data = None
        with open(pcf) as data_file:
            self.raw_pdk_data = json.load(data_file)

        self.original_labels = cell.labels
        self.original_terms = cell.get_polygons(True)[(63, 0)]

        self.labels = list()
        self.maskset = cl.defaultdict(list)
        self.polygons = cl.defaultdict(dict)

    def __str__(self):
        return 'DataField (\"{}\", {} polygons, {} labels)'.format(
            self.name, len(self.polygons.keys()), len(self.labels))

    def deposition(self, mask_poly, params=None, layer=None):
        """
        The layer polygons for each gdsnumber is created in four phases:

        1. Merge all the normal conducting wires.
        2. Merge the polygons inside each component.
        3. Find the difference between the conducting polygons
           and the component polygons.
        4. Add these polygons to the datafield object.

        Parameters
        ----------
        cell_layout : gdspy Cell
            The original layout cell flattened
        datafield : gdspy Cell
            The cell containing all the layer polygons merged

        Arguments
        ---------
        metals : list
            A list containing the points of the merged polygons.
        components : list
            The merged polygons of the specific layer in the components
            that corresponds to the current datatype value.
        """

        utils.green_print('Processing LVS mask polygons')

        def _update_masks(mask_poly, gds):
            from yuna.masks.paths import Path
            from yuna.masks.vias import Via
            from yuna.masks.junctions import Junction
            from yuna.masks.ntrons import Ntron

            if (gds, datatype['path']) in mask_poly:
                p = Path(gds, mask_poly)
                self.maskset[gds].append(p)

                if (gds, datatype['via']) in mask_poly:
                    v = Via(gds, mask_poly)
                    self.maskset[gds].append(v)

                if (gds, datatype['jj']) in mask_poly:
                    j = Junction(gds, mask_poly)
                    self.maskset[gds].append(j)

                if (gds, datatype['ntron']) in mask_poly:
                    n = Ntron(gds, mask_poly)
                    self.maskset[gds].append(n)

        if params is not None:
            for layer_params in params:
                _update_masks(mask_poly, layer_params['layer'])
        elif layer is not None:
            _update_masks(mask_poly, layer)
        else:
            raise ValueError('Both `params` and `layer` cannot be None.')

    def patterning(self, masktype, devtype):
        """
        Once the mask polygons has been placed on the wafer,
        subtract the overlapping edges of the device polygons.

        Parameters
        ----------
        masktype : object
            Mask object, either Path or Via, that will be the subject.
        devtype : object
            Mask object that will be the clipper and is normally a device.
        """

        ee = [sm for gds, mask in self.maskset.items() for sm in mask]
        elements = list(filter(lambda e: isinstance(e, devtype), ee))
        submasks = list(filter(lambda e: isinstance(e, masktype), ee))

        for submask in submasks:
            for element in elements:
                print('submask type - {}'.format(type(submask)))
                print('element type - {}'.format(type(element)))

                submask.diff(element)

    def update(self, devtype=None):
        """
        Update the polygons of all the mask.
        This has to be done in the after depositioning
        to overcome polygon changes as more devies are added.
        """

        for gds, mask_list in self.maskset.items():
            print('... updating mask of type: {}'.format(gds))
            for mask in mask_list:
                if devtype is not None:
                    if isinstance(mask, devtype):
                       mask.add_polygon(self)
                else:
                    mask.add_polygon(self)

    def mask_polygons(self, devtype=None):
        """
        Save the polygon coordinates of all the mask
        objects into a dict datatype.
        """

        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                for pp in mask.polygons:
                    if mask.datatype in self.polygons[gds]:
                        self.polygons[gds][mask.datatype].append(pp)
                    else:
                        self.polygons[gds][mask.datatype] = [pp]

    # def label_cells(self, cell):
    #     """
    #     Label each individual cell before flattening them
    #     to the top-level cell.

    #     Vias are primary components and are detected first.
    #     JJs and nTrons are defined as secondary components.

    #     Returns
    #     -------
    #     out : gdspy Cell
    #         The flattened version of original cell with labeled components
    #     """

    #     if len(cell.elements) == 0:
    #         utils.print_cellrefs(cell)

    #     for subcell in cell.get_dependencies(True):
    #         if subcell.name.split('_')[0] == 'via':
    #             labels.cell.vias(subcell, self)

    #     for subcell in cell.get_dependencies(True):
    #         if subcell.name.split('_')[0] == 'jj':
    #             labels.cell.junctions(subcell, self)

    #     for subcell in cell.get_dependencies(True):
    #         if subcell.name.split('_')[0] == 'ntron':
    #             labels.cell.ntrons(subcell, self)

    # def label_flatten(self, cell_labels):
    #     """
    #     Place the labels to their corresponding positions
    #     after flattening the top-level cell. Update the
    #     datafield object to include all labels in the layout.
    #     """

    #     import yuna.masternodes as mn

    #     utils.green_print('Place labels in flattened layout')

    #     def _add_meta_class(self, lbl, key, layer, name):
    #         params = {}
    #         params['params'] = layer

    #         MyNode = type(name, (MasterNode,), params)

    #         mm = MyNode(text=key, position=lbl.position)

    #         self.labels.append(mm)

    #     for lbl in cell_labels:
    #         comp = lbl.text.split('_')[0]

    #         if comp == 'via':

    #             print('Flatterning Via labels...')

    #             for key, layer in self.raw_pdk_data['Cells']['Vias'].items():
    #                 if key != 'color' and key == lbl.text:
    #                     _add_meta_class(self, lbl, key, layer, 'Via')

    #             # params = self.raw_pdk_data['Cells']['Vias'][lbl.text]
    #             # params['text'] = lbl.text
    #             # params['layer'] = 63

    #             # via = mn.via.Via(lbl.position, params)
    #             # self.labels.append(via)

    #         if comp == 'ntron':
    #             print('Flatterning Via labels...')

    #             for key, layer in self.raw_pdk_data['Cells']['Ntrons'].items():
    #                 if key != 'color' and key == lbl.text:
    #                     _add_meta_class(self, lbl, key, layer, 'Ntron')

    #             # params = self.raw_pdk_data['Cells']['Ntrons'][lbl.text]
    #             # params['text'] = lbl.text
    #             # params['layer'] = 63

    #             # ntron = mn.ntron.Ntron(lbl.position, params)
    #             # self.labels.append(ntron)

    #         # if comp == 'jj':
    #         #     params = self.raw_pdk_data['Cells']['Junctions']
    #         #     params['text'] = lbl.text
    #         #
    #         #     jj = mn.junction.Junction(lbl.position, params)
    #         #     self.labels.append(jj)
    #         #
    #         # if comp == 'shunt':
    #         #     params = self.raw_pdk_data['Cells']['Ntrons']
    #         #     params['text'] = lbl.text
    #         #
    #         #     shunt = mn.junction.Shunt(lbl.position, params)
    #         #     self.labels.append(shunt)
    #         #
    #         # if comp == 'ground':
    #         #     params = self.raw_pdk_data['Cells']['Ntrons']
    #         #     params['text'] = lbl.text
    #         #
    #         #     ground = mn.junction.Ground(lbl.position, params)
    #         #     self.labels.append(ground)

    def user_label_cap(self, cell):
        from yuna.masternodes.capacitor import Capacitor

        for lbl in cell.labels:
            if lbl.text[0] == 'C':
                params = self.raw_pdk_data['Structure']['Capacitor']
                params['text'] = lbl.text
                params['layer'] = lbl.layer
                params['ports'] = utils.calculate_ports(lbl.text.split(' '),
                                                         self.raw_pdk_data)

                cap = Capacitor(lbl.position, params)
                self.labels.append(cap)

    def user_label_term(self, cell):
        from yuna.masternodes.terminal import Terminal

        for lbl in cell.labels:
            if lbl.text[0] == 'P':
                params = self.raw_pdk_data['Structure']['Terminal']['63']
                params['text'] = lbl.text
                params['layer'] = lbl.layer
                params['ports'] = utils.calculate_ports(lbl.text.split(' '),
                                                         self.raw_pdk_data)

                term = Terminal(lbl.position, params)
                self.labels.append(term)

    def has_device(self, dtype):
        for label in self.labels:
            if isinstance(label, dtype):
                return True
        return False

    # def get_terminals(self):
    #     terminals = dict()
    #
    #     for gds, polydata in self.polygons.items():
    #         for datatype, polygons in polydata.items():
    #             for poly in polygons:
    #                 if poly.data.type == 'term':
    #                     key = (gds, datatype)
    #                     if key in terminals:
    #                         terminals[key].append(np.array(poly.points))
    #                     else:
    #                         terminals[key] = [np.array(poly.points)]
    #
    #     return terminals

    # def get_metals(self):
    #     metals = dict()
    #
    #     for gds, polydata in self.polygons.items():
    #         for datatype, polygons in polydata.items():
    #             for poly in polygons:
    #                 if poly.data.type in ['ix', 'res']:
    #                     key = (gds, datatype)
    #                     if key in metals:
    #                         metals[key].append(np.array(poly.points))
    #                     else:
    #                         metals[key] = [np.array(poly.points)]
    #
    #     return metals

    def gds_auron(self, cell):
        from yuna.masks.paths import Path
        from yuna.masks.vias import Via
        from yuna.masks.junctions import Junction
        from yuna.masks.ntrons import Ntron

        def _update_cell(mask):
            for pp in mask.polygons:
                polygon = gdspy.Polygon(*pp.get_variables())
                cell.add(polygon)

        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                if isinstance(mask, Path):
                    _update_cell(mask)
                elif isinstance(mask, Via):
                    _update_cell(mask)
                elif isinstance(mask, Junction):
                    _update_cell(mask)
                elif isinstance(mask, Ntron):
                    _update_cell(mask)

        for label in self.labels:
            lbl = label.get_label()
            cell.add(lbl)

    def gds_inductex(self, cell):
        from yuna.masks.paths import Path
        from yuna.masks.vias import Via
        from yuna.masks.junctions import Junction
        from yuna.masks.ntrons import Ntron

        for poly in self.original_terms:
            polygon = gdspy.Polygon(poly, 63, 0)
            cell.add(polygon)

        def _update_cell(mask):
            for pp in mask.polygons:
                polygon = gdspy.Polygon(*pp.get_variables())
                cell.add(polygon)

        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                if isinstance(mask, Path):
                    _update_cell(mask)
                elif isinstance(mask, Via):
                    _update_cell(mask)
                elif isinstance(mask, Junction):
                    _update_cell(mask)
                elif isinstance(mask, Ntron):
                    _update_cell(mask)

        for label in self.original_labels:
            cell.add(label)
