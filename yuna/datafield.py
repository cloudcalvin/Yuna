import gdsyuna
import yuna
import numpy as np
import os, sys, json
import collections as cl

from yuna import tools
from yuna import process


class DataField(gdsyuna.Cell):

    def __init__(self, name, pcf):
        self.name = name
        self.pcd = self.read_config(pcf)

        self.polygons = cl.defaultdict(dict)
        self.labels = list()

    def add_junction_component(self, fabdata):
        gds = fabdata['Atoms']['jjs']['gds']
        name = fabdata['Atoms']['jjs']['name']
        layers = fabdata['Atoms']['jjs']['layers']
        color = fabdata['Atoms']['jjs']['color']

        jj = process.Junction(gds, name, layers, color)

        jj.add_position(fabdata)
        jj.add_width(fabdata)
        jj.add_shunt_data(fabdata)
        jj.add_ground_data(fabdata)

        return jj

    def read_config(self, pcf):
        """ Reads the config file that is written in
        JSON. This file contains the logic of how
        the different layers will interact. """

        fabdata = None
        with open(pcf) as data_file:
            fabdata = json.load(data_file)

        pcd = process.ProcessData()

        pcd.add_parameters(fabdata['Params'])
        pcd.add_atoms(fabdata['Atoms'])

        for mtype in ['ix', 'res', 'via', 'jj']:
            for gds, value in fabdata[mtype].items():
                pcd.add_layer(mtype, int(gds), value)

        jj = self.add_junction_component(fabdata)
        pcd.add_component(jj)

        return pcd

    # def get_polygons(self):
    #     polygons = {}
    #     for poly in self.polygons:
    #         key = (poly.layer, poly.datatype)
    #         pp = tools.convert_node_to_3d([poly.points], 0)
    #         if key in polygons:
    #             polygons[key].append(pp)
    #         else:
    #             polygons[key] = [pp]
    #     return polygons

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

        print('--------' + str(type(element)))
        if isinstance(element, Label):
            self.labels.append(element)
        else:
            fabdata = {0: [self.pcd.layers['ix'], self.pcd.layers['res']],
                       1: [self.pcd.layers['via']],
                       3: [self.pcd.layers['jj']]}

            polygon = Polygon(key, element, fabdata)
            if key[1] in self.polygons[key[0]]:
                self.polygons[key[0]][key[1]].append(polygon)
            else:
                self.polygons[key[0]][key[1]] = [polygon]

            # if key in self.polygons:
            #     self.polygons[key].append(polygon)
            # else:
            #     self.polygons[key] = [polygon]

        return self

    def parse_gdspy(self, cell):

        for i in [34, 6, 9]:
            for key, poly in self.polygons[i].items():
                for pp in poly:
                    polygon = gdsyuna.Polygon(*pp.get_variables())
                    cell.add(polygon)

        for lbl in self.labels:
            label = gdsyuna.Label(*lbl.get_variables())
            cell.add(label)


class Polygon(gdsyuna.Polygon):
    _ID = 0

    def __init__(self, key, points, fabdata):
        super(Polygon, self).__init__(points, *key, verbose=False)

        self.id = 'p{}'.format(Polygon._ID)
        Polygon._ID += 1

        gds, datatype = key[0], key[1]

        self.data = None
        for layers in fabdata[datatype]:
            if gds in layers.keys():
                self.data = layers[gds]

    def get_points(self, width=0):
        polygons = []
        layer = np.array([self.points]).tolist()
        for pl in layer:
            poly = [[float(y*10e-9) for y in x] for x in pl]
            for row in poly:
                row.append(width)
            polygons.append(poly)
        return [polygons]

    def get_variables(self):
        return (self.points, self.layer, self.datatype)


class Label(gdsyuna.Label):
    _ID = 0

    def __init__(self, ttype, metals, text, position, rotation, layer):
        super(Label, self).__init__(text, position, rotation=rotation, layer=layer)

        self.id = 'l{}'.format(Label._ID)
        self.type = ttype
        self.metals = metals

    def get_variables(self):
        return (self.text, self.position, self.rotation, self.layer)
