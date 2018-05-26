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


logger = logging.getLogger(__name__)


class Geometry(object):

    def __init__(self, name, pcf):
        self.name = name

        if pcf is not None:
            self.pcd = self.read_config(pcf)

        self.labels = list()
        self.maskset = cl.defaultdict(list)
        self.polygons = cl.defaultdict(dict)

    def __str__(self):
        return "DataField (\"{}\", {} polygons, {} labels)".format(
            self.name, len(self.polygons.keys()), len(self.labels))

    def read_config(self, pcf):
        """ Reads the config file that is written in
        JSON. This file contains the logic of how
        the different layers will interact. """

        fabdata = None
        with open(pcf) as data_file:
            fabdata = json.load(data_file)

        pcd = process.ProcessConfigData()

        pcd.add_parameters(fabdata['Params'])
        pcd.add_atoms(fabdata['Atoms'])

        for mtype in ['ix', 'hole', 'res', 'via', 'jj', 'term', 'ntron', 'cap']:
            if mtype in fabdata:
                for gds, value in fabdata[mtype].items():
                    pcd.add_layer(mtype, int(gds), value)
        return pcd

    def deposition(self, cell):
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

        from yuna.masks.paths import Path
        from yuna.masks.vias import Via
        from yuna.masks.junctions import Junction
        from yuna.masks.ntrons import Ntron

        utils.green_print('Processing LVS mask polygons')

        cell_layout = cell.copy('Polygon Flatten',
                                exclude_from_current=True,
                                deep_copy=True)
        cell_layout.flatten()

        wires = {**self.pcd.layers['ix'],
                 **self.pcd.layers['res']}

        def _etl_polygons(wires, cell):
            """
            Reads throught the PDF file and converts the corresponding
            conducting layers to the same type. An example of this is
            layer NbN_1 and NbN_2 that should be the same.

            Output : dict()
                Updated `poly` version that has converted the ETL polygons.
            """

            logger.info('ETL Polygons')

            pp = cell.get_polygons(True)

            ply = cl.defaultdict(list)

            for gds, ll in wires.items():
                if ll.etl is not None:
                    p = {(ll.etl, k[1]): v for k, v in pp.items() if gds == k[0]}
                else:
                    p = {k: v for k, v in pp.items() if gds == k[0]}

                for k, v in p.items():
                    ply[k].extend(v)
            return ply

        mask_poly = _etl_polygons(wires, cell_layout)

        for gds, layer in wires.items():
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

    def patterning(self, masktype, devtype):
        """

        """

        ee = [sm for gds, mask in self.maskset.items() for sm in mask]
        elements = list(filter(lambda e: isinstance(e, devtype), ee))
        submasks = list(filter(lambda e: isinstance(e, masktype), ee))

        for submask in submasks:
            for element in elements:
                submask.add(element)

    def update_polygons(self, devtype=None):

        def _save_polygons():
            for gds, mask_list in self.maskset.items():
                for mask in mask_list:
                    for pp in mask.polygons:
                        if mask.datatype in self.polygons[gds]:
                            self.polygons[gds][mask.datatype].append(pp)
                        else:
                            self.polygons[gds][mask.datatype] = [pp]

        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                if devtype is None:
                    mask.update_mask(self)
                else:
                    if isinstance(mask, devtype):
                       mask.update_mask(self)

        _save_polygons()

    def label_cells(self, cell):
        """
        Label each individual cell before flattening them
        to the top-level cell.

        Vias are primary components and are detected first.
        JJs and nTrons are defined as secondary components.

        Returns
        -------
        out : gdspy Cell
            The flattened version of original cell with labeled components
        """

        if len(cell.elements) == 0:
            utils.print_cellrefs(cell)

        for subcell in cell.get_dependencies(True):
            if subcell.name.split('_')[0] == 'via':
                labels.cell.vias(subcell, self)

        for subcell in cell.get_dependencies(True):
            if subcell.name.split('_')[0] == 'jj':
                labels.cell.junctions(subcell, self)

        for subcell in cell.get_dependencies(True):
            if subcell.name.split('_')[0] == 'ntron':
                labels.cell.ntrons(subcell, self)

    def label_flatten(self, cell):
        """
        Place the labels to their corresponding positions
        after flattening the top-level cell. Update the
        datafield object to include all labels in the layout.
        """

        import yuna.masternodes as mn

        utils.green_print('Place labels in flattened layout')

        cl = cell.copy('Label Flatten',
                       exclude_from_current=True,
                       deep_copy=True)

        cell_labels = cl.flatten().get_labels(0)

        if len(cell_labels) > 0:
            for label in cell_labels:
                logging.info(label.text)

        for lbl in cell_labels:
            comp = lbl.text.split('_')[0]

            if comp == 'via':
                via = mn.via.Via(lbl.text,
                                 lbl.position,
                                 atom=self.pcd.atoms['vias'])

                self.labels.append(via)

            if comp == 'jj':
                jj = mn.junction.Junction(lbl.text,
                                          lbl.position,
                                          atom=self.pcd.atoms['jjs'])

                self.labels.append(jj)

            if comp == 'ntron':
                ntron = mn.ntron.Ntron(lbl.text,
                                       lbl.position,
                                       atom=self.pcd.atoms['ntrons'])

                self.labels.append(ntron)

            if comp == 'shunt':
                shunt = mn.junction.Shunt(lbl.text,
                                          lbl.position,
                                          atom=self.pcd.atoms['jjs'])

                self.labels.append(shunt)

            if comp == 'ground':
                ground = mn.junction.Ground(lbl.text,
                                            lbl.position,
                                            atom=self.pcd.atoms['jjs'])

                self.labels.append(ground)

    def user_label_cap(self, cell):
        from yuna.masternodes.capacitor import Capacitor
        for lbl in cell.labels:
            if lbl.text[0] == 'C':
                cap = Capacitor(self.pcd.layers['cap'],
                                lbl.text,
                                lbl.position,
                                lbl.layer)

                cap.set_plates(self)
                cap.metal_connection(self)
                self.labels.append(cap)

    def user_label_term(self, cell):
        from yuna.masternodes.terminal import Terminal
        for lbl in cell.labels:
            if lbl.text[0] == 'P':
                term = Terminal(self.pcd.layers['term'],
                                lbl.text,
                                lbl.position,
                                lbl.layer)

                term.metal_connection(self)
                self.labels.append(term)

    def has_device(self, dtype):
        for label in self.labels:
            if isinstance(label, dtype):
                return True
        return False

    def get_terminals(self):
        terminals = dict()

        for gds, polydata in self.polygons.items():
            for datatype, polygons in polydata.items():
                for poly in polygons:
                    if poly.data.type == 'term':
                        key = (gds, datatype)
                        if key in terminals:
                            terminals[key].append(np.array(poly.points))
                        else:
                            terminals[key] = [np.array(poly.points)]

        return terminals

    def get_metals(self):
        metals = dict()

        for gds, polydata in self.polygons.items():
            for datatype, polygons in polydata.items():
                for poly in polygons:
                    if poly.data.type in ['ix', 'res']:
                        key = (gds, datatype)
                        if key in metals:
                            metals[key].append(np.array(poly.points))
                        else:
                            metals[key] = [np.array(poly.points)]

        return metals

    def parse_gdspy(self, cell):
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
