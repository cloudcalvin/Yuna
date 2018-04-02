import gdsyuna
import pprint
import yuna
import numpy as np
import os
import sys
import json
import collections as cl

from yuna import tools
from yuna import process


nm = 10e-9


class DataField(object):

    def __init__(self, name, pcf):
        self.name = name

        self.pcd, self.wires, self.nonwires = self.read_config(pcf)

        self.mask = cl.defaultdict(dict)
        self.polygons = cl.defaultdict(dict)
        self.labels = cl.defaultdict(dict)

    def __str__(self):
        return "DataField (\"{}\", {} polygons, {} labels)".format(
            self.name, len(self.polygons.keys()),len(self.labels))

#     def add_junction_component(self, fabdata):
#         gds = fabdata['Atoms']['jjs']['gds']
#         name = fabdata['Atoms']['jjs']['name']
#         layers = fabdata['Atoms']['jjs']['layers']
#         color = fabdata['Atoms']['jjs']['color']
#
#         jj = process.Junction(gds, name, layers, color)
#
#         jj.add_position(fabdata)
#         jj.add_width(fabdata)
#         jj.add_shunt_data(fabdata)
#         jj.add_ground_data(fabdata)
#
#         return jj

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

        for mtype in ['ix', 'hole', 'res', 'via', 'jj', 'term', 'ntron']:
            if mtype in fabdata:
                for gds, value in fabdata[mtype].items():
                    pcd.add_layer(mtype, int(gds), value)

        wires = {**pcd.layers['ix'],
                 **pcd.layers['res'],
                 **pcd.layers['term']}

        nonwires = {**pcd.layers['via'],
                    **pcd.layers['hole'],
                    **pcd.layers['jj'],
                    **pcd.layers['ntron']}

        return pcd, wires, nonwires

    def add_mask(self, element, key=None, holes=None):
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

        if key is None:
            raise TypeError('key cannot be None')

        assert isinstance(element[0], list)

        fabdata = {**self.pcd.layers['ix'],
                   **self.pcd.layers['hole'],
                   **self.pcd.layers['res'],
                   **self.pcd.layers['term'],
                   **self.pcd.layers['via'],
                   **self.pcd.layers['jj'],
                   **self.pcd.layers['ntron']}

        polygon = Polygon(key, element, fabdata, holes)

        if key[1] in self.mask[key[0]]:
            self.mask[key[0]][key[1]].append(polygon)
        else:
            self.mask[key[0]][key[1]] = [polygon]

    def add(self, element, key=None):
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

        if key is None:
            raise TypeError('key cannot be None')

        assert isinstance(element[0], list)

        fabdata = {**self.pcd.layers['ix'],
                   **self.pcd.layers['hole'],
                   **self.pcd.layers['res'],
                   **self.pcd.layers['term'],
                   **self.pcd.layers['via'],
                   **self.pcd.layers['jj'],
                   **self.pcd.layers['ntron']}

        polygon = Polygon(key, element, fabdata)

        if key[1] in self.polygons[key[0]]:
            self.polygons[key[0]][key[1]].append(polygon)
        else:
            self.polygons[key[0]][key[1]] = [polygon]

    def parse_gdspy(self, cell):

        for i in self.wires:
            for key, poly in self.polygons[i].items():
                for pp in poly:
                    polygon = gdsyuna.Polygon(*pp.get_variables())
                    cell.add(polygon)

        # for i in self.nonwires:
        #     for key, poly in self.mask[i].items():
        #         for pp in poly:
        #             polygon = gdsyuna.Polygon(*pp.get_variables())
        #             cell.add(polygon)

        # for tt, value in self.pcd.layers.items():
        #     for i, value2 in value.items():
        #         for key, poly in self.mask[i].items():
        #             for pp in poly:
        #                 polygon = gdsyuna.Polygon(*pp.get_variables())
        #                 cell.add(polygon)

        for lbl in self.labels:
            for key, value in self.labels.items():
                for label in value['labels']:
                    cell.add(label)


class Polygon(gdsyuna.Polygon):
    """
    Holes can only be a list of points, since it is only a hole
    and has no other properties.
    """

    _ID = 0

    def __init__(self, key, points, fabdata, holes=None):
        super(Polygon, self).__init__(points, *key, verbose=False)

        self.holes = holes

        self.id = 'p{}'.format(Polygon._ID)
        Polygon._ID += 1

        self.data = fabdata[int(key[0])]

        if self.data is None:
            raise ValueError('Polygon data cannot be None.')

    def get_holes(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.holes]

    def get_points(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.points]

    def get_variables(self):
        return (self.points, self.layer, self.datatype)


# class Label(gdsyuna.Label):
#     _ID = 0
#
#     def __init__(self, metals, text, position, rotation=0, layer=0):
#         super(Label, self).__init__(text, position, rotation=rotation, layer=layer)
#
#         self.id = 'l{}'.format(Label._ID)
#         Label._ID += 1
#
#         # pre_label = text.split('_')[0]
#
#         # tt = ['P', 'via', 'jj', 'sht', 'gnd']
#         # if pre_label in tt:
#         #     self.type = pre_label
#         # else:
#         #     self.type = None
#         #
#         # if self.type is None:
#         #     raise TypeError("label type cannot be None")
#
#         self.metals = metals
#
#     def update_position(self, position):
#         self.position = position
#
#     def get_variables(self):
#         return (self.text, self.position, 'nw',
#                 self.rotation, 0, False, self.layer)
