import gdspy
import pprint
import yuna
import numpy as np
import os
import sys
import json
import collections as cl

from yuna import utils
from yuna import process

from .utils import nm
from .utils import logging

logger = logging.getLogger(__name__)


class DataField(object):

    def __init__(self, name, pcf):
        self.name = name

        if pcf is not None:
            self.pcd = self.read_config(pcf)

        self.mask = cl.defaultdict(dict)
        self.polygons = cl.defaultdict(dict)
        self.labels = list()

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

    def add(self, element, key=None, holes=None, model='lvs'):
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

        if model == 'lvs':
            if key[1] in self.polygons[key[0]]:
                self.polygons[key[0]][key[1]].append(polygon)
            else:
                self.polygons[key[0]][key[1]] = [polygon]
        elif model == 'model':
            if key[1] in self.mask[key[0]]:
                self.mask[key[0]][key[1]].append(polygon)
            else:
                self.mask[key[0]][key[1]] = [polygon]

    def parse_gdspy(self, cell):
        wires = {**self.pcd.layers['ix'],
                 **self.pcd.layers['term'],
                 **self.pcd.layers['res']}

        for i in wires:
            for key, poly in self.polygons[i].items():
                for pp in poly:
                    polygon = gdspy.Polygon(*pp.get_variables())
                    cell.add(polygon)

        for label in self.labels:
            lbl = label.get_label()
            cell.add(lbl)

        # for lbl in self.labels:
        #     for key, value in self.labels.items():
        #         print(key, value)
        #         for label in value['labels']:
        #             cell.add(label)


class Polygon(gdspy.Polygon):
    """
    Holes can only be a list of points, since it is only a hole
    and has no other properties.
    """

    _ID = 0

    def __init__(self, key, points, fabdata, holes=None):
        super(Polygon, self).__init__(points, *key, verbose=False)

        self.holes = holes

        if key[1] == 1:
            self.id = 'v{}'.format(Polygon._ID)
        elif key[1] == 3:
            self.id = 'j{}'.format(Polygon._ID)
        elif key[1] == 7:
            self.id = 'n{}'.format(Polygon._ID)
        else:
            self.id = 'i{}'.format(Polygon._ID)

        Polygon._ID += 1

        self.data = fabdata[int(key[0])]

        assert isinstance(self.data.name, str)

        if self.data is None:
            raise ValueError('Polygon data cannot be None.')

    def get_holes(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.holes]

    def get_points(self, z):
        return [[float(p[0]*nm), float(p[1]*nm), z] for p in self.points]

    def get_variables(self):
        return (self.points, self.layer, self.datatype)
