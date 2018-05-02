import numpy as np
import networkx as nx
import itertools
import gdspy
import pyclipper

from yuna import utils

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from collections import namedtuple
from collections import defaultdict

from yuna import masternodes as mn
from yuna import cell_labels as cl


class Metal(object):

    def __init__(self, gds, poly):
        self.key = (gds, 0)
        self.raw_points = poly[(gds, 0)]
        self.points = self.union()

    def union(self):
        if not isinstance(self.raw_points[0][0], np.ndarray):
            raise TypeError("poly must be a 3D list")

        cc_poly = list()

        for poly in self.raw_points:
            if pyclipper.Orientation(poly) is False:
                reverse_poly = pyclipper.ReversePath(poly)
                cc_poly.append(reverse_poly)
            else:
                cc_poly.append(poly)

        union = utils.angusj(subj=cc_poly, method='union')
        points = pyclipper.CleanPolygons(union)

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def create_mask(self, datafield, myCell):

        named_layers = defaultdict(dict)

        for l1 in self.points:
            Polygon = namedtuple('Polygon', ['area', 'points'])
            pp = Polygon(area=pyclipper.Area(l1), points=l1)

            if pp.area < 0:
                if 'holes' in named_layers:
                    named_layers['holes'].append(pp)
                else:
                    named_layers['holes'] = [pp]
            elif pp.area > 0:
                if 'polygon' in named_layers:
                    named_layers['polygon'].append(pp)
                else:
                    named_layers['polygon'] = [pp]
            else:
                raise ValueError('polygon area cannot be zero')

        for poly in named_layers['polygon']:
            add_to_mask = True

            for hole in named_layers['holes']:
                if abs(hole.area) < abs(poly.area):

                    if utils.is_nested_polygons(hole, poly):
                        datafield.add(poly.points, self.key, holes=hole.points, model='model')
                        myCell.add(gdspy.Polygon(hole.points, layer=81))
                        add_to_mask = False
                    else:
                        datafield.add(poly.points, self.key, model='model')
                        add_to_mask = False

            if add_to_mask:
                datafield.add(poly.points, self.key, model='model')

            myCell.add(gdspy.Polygon(poly.points, self.key[0], verbose=False))

    def add(self, element):
        self.points = utils.angusj(self.points, element.points, 'difference')

    def update_mask(self, datafield):
        for pp in self.points:
            datafield.add(pp, self.key)


class Via(object):

    def __init__(self, gds, poly):
        self.clip = False
        self.key = (gds, 1)
        self.raw_points = poly[(gds, 1)]
        self.points = self.union()

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield, element=None):
        if element is not None:
            self.points = utils.angusj(self.points, element.points, 'difference')

        for pp in self.points:
            datafield.add(pp, self.key)

        self.clip = True


class Junction(object):

    def __init__(self, gds, poly):
        self.key = (gds, 3)
        self.raw_points = poly[(gds, 3)]
        self.points = self.union()

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield):
        for pp in self.points:
            datafield.add(pp, self.key)


class Ntron(object):

    def __init__(self, gds, poly):
        self.key = (gds, 7)
        self.raw_points = poly[(gds, 7)]
        self.points = self.union()

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield):
        for pp in self.points:
            datafield.add(pp, self.key)


def add_cell_components(cell, datafield):
    """
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
            cl.vias(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'jj':
            cl.junctions(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'ntron':
            cl.ntrons(subcell, datafield)


def add_flatten_components(cell_flat, datafield):
    pass

    # for element in cell_flat.elements:
    #     if isinstance(element, gdspy.PolygonSet):
    #         if element.layers[0] == 65:
    #             for points in element.polygons:
    #                 polygon = gdspy.Polygon(points, 65)
    #                 labels.add_label(cell_flat, polygon, 'cap', datafield)


def update_datafield_labels(cell_flat, datafield):

    cell_labels = cell_flat.get_labels(0)

    if len(cell_labels) > 0:
        utils.print_labels(cell_labels)

    for lbl in cell_labels:
        comp = lbl.text.split('_')[0]

        if comp == 'via':
            via = mn.Via(lbl.text, lbl.position, atom=datafield.pcd.atoms['vias'])
            datafield.labels.append(via)

        if comp == 'jj':
            jj = mn.Junction(lbl.text, lbl.position, atom=datafield.pcd.atoms['jjs'])
            datafield.labels.append(jj)

        if comp == 'ntron':
            ntron = mn.Ntron(lbl.text, lbl.position, atom=datafield.pcd.atoms['ntrons'])
            datafield.labels.append(ntron)

        if comp == 'shunt':
            shunt = mn.Shunt(lbl.text, lbl.position, atom=datafield.pcd.atoms['jjs'])
            datafield.labels.append(shunt)

        if comp == 'ground':
            ground = mn.Ground(lbl.text, lbl.position, atom=datafield.pcd.atoms['jjs'])
            datafield.labels.append(ground)


def lvs_mask(cell, datafield):
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

    cell_layout = cell.copy('Polygon Flatten', deep_copy=True)
    cell_layout.flatten()

    poly = cell_layout.get_polygons(True)

    metals = defaultdict(dict)

    wires = {**datafield.pcd.layers['ix'],
             **datafield.pcd.layers['res']}

    for gds, layer in wires.items():
        if (gds, 0) in poly:
            metals[gds] = Metal(gds, poly)

    vias = defaultdict(dict)
    jjs = defaultdict(dict)
    ntrons = defaultdict(dict)

    for gds, layer in wires.items():
        if gds in metals:
            if (gds, 1) in poly:
                via = Via(gds, poly)
                # via.update_mask(datafield)
                vias[gds] = via

            if (gds, 3) in poly:
                jj = Junction(gds, poly)
                # jj.update_mask(datafield)
                jjs[gds] = jj

            if (gds, 7) in poly:
                ntron = Ntron(gds, poly)
                # ntron.update_mask(datafield)
                ntrons[gds] = ntron

    # # TODO: We use a dict so that we can do individual unittests like this.
    # metals[6].add(vias[6])
    # metals[6].update_mask(datafield)

    for gds, metal in metals.items():
        if gds in vias:
            metal.add(vias[gds])

    # for gds, metal in metals.items():
    #     if gds in jjs:
    #         metal.add(jjs[gds])

    for gds, metal in metals.items():
        if gds in ntrons:
            metal.add(ntrons[gds])

            ntron.update_mask(datafield)

            if gds in vias:
                via.update_mask(datafield, ntrons[gds])

    for gds, via in vias.items():
        if via.clip is False:
            via.update_mask(datafield)

    for gds, metal in metals.items():
        metal.update_mask(datafield)


def model_mask(cell, datafield):
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

    myCell = gdspy.Cell('myCell')

    cell_origin = cell.copy('Original', deep_copy=True)
    cell_origin.flatten()

    poly = cell_origin.get_polygons(True)

    mask_layers = {**datafield.pcd.layers['ix'],
                   **datafield.pcd.layers['term'],
                   **datafield.pcd.layers['res'],
                   **datafield.pcd.layers['via'],
                   **datafield.pcd.layers['jj'],
                   **datafield.pcd.layers['ntron']}

    metals = defaultdict(dict)

    for gds, layer in mask_layers.items():
        if (gds, 0) in poly:
            metals[gds] = Metal(gds, poly)
            metals[gds].create_mask(datafield, myCell)
