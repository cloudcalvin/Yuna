import gdspy
import pprint
import yuna
import numpy as np
import os
import sys
import json
import collections as cl

from yuna import process

from yuna.utils import nm
from yuna.utils import logging

import yuna.devices as devices

logger = logging.getLogger(__name__)


class DataField(object):

    def __init__(self, name, pcf):
        self.name = name

        if pcf is not None:
            self.pcd = self.read_config(pcf)

        self.maskset = dict()
        self.labels = list()
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

    def add_mask(self, gds, mask):
        if gds in self.maskset:
            self.maskset[gds].append(mask)
        else:
            self.maskset[gds] = [mask]

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

    def pattern_path(self, device_type):
        elements = []
        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, device_type):
                    elements.append(submask)

        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, devices.paths.Path):
                    for element in elements:
                        submask.add(element)

    def pattern_via(self, device_type):
        elements = []
        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, device_type):
                    elements.append(submask)

        for gds, mask in self.maskset.items():
            for submask in mask:
                if isinstance(submask, devices.vias.Via):
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
                if isinstance(mask, devices.paths.Path):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)
                elif isinstance(mask, devices.vias.Via):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)
                elif isinstance(mask, devices.junctions.Junction):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)
                elif isinstance(mask, devices.ntrons.Ntron):
                    for pp in mask.polygons:
                        polygon = gdspy.Polygon(*pp.get_variables())
                        cell.add(polygon)

        for label in self.labels:
            lbl = label.get_label()
            cell.add(lbl)


# class Polygon(gdspy.Polygon):
#     """
#     Holes can only be a list of points, since it is only a hole
#     and has no other properties.
#     """
#
#     _ID = 0
#
#     def __init__(self, key, points, fabdata, holes=None):
#         super(Polygon, self).__init__(points, *key, verbose=False)
#
#         self.holes = holes
#
#         if key[1] == 1:
#             self.id = 'v{}'.format(Polygon._ID)
#         elif key[1] == 3:
#             self.id = 'j{}'.format(Polygon._ID)
#         elif key[1] == 7:
#             self.id = 'n{}'.format(Polygon._ID)
#         else:
#             self.id = 'i{}'.format(Polygon._ID)
#
#         Polygon._ID += 1
#
#         self.data = fabdata[int(key[0])]
#
#         assert isinstance(self.data.name, str)
#
#         if self.data is None:
#             raise ValueError('Polygon data cannot be None.')
#
#     def get_holes(self, z):
#         return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.holes]
#
#     def get_points(self, z):
#         return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.points]
#
#     def get_variables(self):
#         return (self.points, self.layer, self.datatype)
