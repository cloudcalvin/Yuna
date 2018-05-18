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

from yuna.masks.paths import Path
from yuna.masks.vias import Via
from yuna.masks.junctions import Junction
from yuna.masks.ntrons import Ntron


logger = logging.getLogger(__name__)


class DataField(object):

    def __init__(self, name, pcf):
        self.name = name

        if pcf is not None:
            self.pcd = self.read_config(pcf)

        self.labels = list()
        self.maskset = cl.defaultdict(list)
        self.polygons = cl.defaultdict(dict)

    def __str__(self):
        return "DataField (\"{}\", {} polygons, {} labels)".format(
            self.name, len(self.polygons.keys()),len(self.labels))

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

    def get_polygons(self):
        """
        Add a new element or list of elements to this cell.

        Parameters
        ----------
        element : object
            The element or list of elements to be inserted in this cell.

        Returns
        -------
        out : ``Cell``
            This cell.
        """

        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                for polygon in mask.polygons:
                    if mask.datatype in self.polygons[gds]:
                        self.polygons[gds][mask.datatype].append(polygon)
                    else:
                        self.polygons[gds][mask.datatype] = [polygon]

    def _filter_elements(self, devtype):
        elements = []
        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, devtype):
                    elements.append(submask)
        return elements

    def pattern_path(self, devtype):
        elements = self._filter_elements(devtype)

        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, Path):
                    for element in elements:
                        submask.add(element)

    def pattern_via(self, devtype):
        elements = self._filter_elements(devtype)

        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, Via):
                    for element in elements:
                        submask.add(element)

    def update_polygons(self, device_type=None):
        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                if device_type is None:
                    mask.update_mask(self)
                else:
                    if isinstance(mask, device_type):
                       mask.update_mask(self)
        self.get_polygons()

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
        for gds, mask_list in self.maskset.items():
            for mask in mask_list:
                if isinstance(mask, Path):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)
                elif isinstance(mask, Via):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)
                elif isinstance(mask, Junction):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)
                elif isinstance(mask, Ntron):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)

        for label in self.labels:
            lbl = label.get_label()
            cell.add(lbl)

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

        utils.green_print('Processing LVS mask polygons')

        cell_layout = cell.copy('Polygon Flatten', deep_copy=True)
        cell_layout.flatten()

        wires = {**self.pcd.layers['ix'],
                 **self.pcd.layers['res']}

        # Mask = namedtuple('Mask', ['dtype', 'devices'])

        # paths = Mask(dtype=datatype['path'], element=[])
        # vias = Mask(dtype=datatype['via'], element=[])
        # jjs = Mask(dtype=datatype['jj'], element=[])
        # ntrons = Mask(dtype=datatype['ntron'], element=[])

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
                    p = {(ll.etl, k[1]):v for k,v in pp.items() if gds == k[0]}
                else:
                    p = {k:v for k,v in pp.items() if gds == k[0]}

                for k,v in p.items():
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
