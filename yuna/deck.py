import numpy as np
import networkx as nx
import itertools
import json
import gdsyuna
import pyclipper

from yuna import labels
from yuna import connect
from yuna import tools

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import collections as cl
from collections import namedtuple


def components(cell, datafield):
    """
    Vias are primary components and are detected first.
    JJs and nTrons are defined as secondary components.

    Returns
    -------
    out : gdspy Cell
        The flattened version of original cell with labeled components
    """

    tools.print_cellrefs(cell)

    labels.terminals(cell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name[:3] == 'via':
            labels.vias(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name[:2] == 'jj':
            labels.junctions(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name[:5] == 'ntron':
            labels.ntrons(subcell, datafield)

    cell_layout = cell.copy('Label Flatten', deep_copy=True)
    cell_layout.flatten()

    cell_labels = cell_layout.get_labels(0)

    for lbl in cell_labels:
        if 'labels' in datafield.labels[lbl.text]:
            datafield.labels[lbl.text]['labels'].append(lbl)
        else:
            datafield.labels[lbl.text]['labels'] = []
            datafield.labels[lbl.text]['labels'].append(lbl)


def add_vias(gds, datatype, datafield, poly, metals):
    dkey = (gds, datatype)
    if dkey in poly:
        components = tools.angusj(poly[dkey], poly[dkey], 'union')

        for pp in components:
            datafield.add(pp, dkey)

        metals = tools.angusj(components, metals, 'difference')
    return metals


def add_junctions(gds, datatype, datafield, poly, metals):
    dkey = (gds, datatype)
    if dkey in poly:
        components = tools.angusj(poly[dkey], poly[dkey], 'union')

        for pp in components:
            datafield.add(pp, dkey)

        metals = tools.angusj(components, metals, 'difference')
    return metals


def add_ntrons(gds, datatype, datafield, poly, metals):
    dkey = (gds, datatype)
    if dkey in poly:
        components = tools.angusj(poly[dkey], poly[dkey], 'union')

        for pp in components:
            datafield.add(pp, dkey)

        metals = tools.angusj(components, metals, 'difference')
    return metals


def layers(cell, datafield):
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

    for gds, layer in datafield.wires.items():
        for i in [0, 1, 3, 7]:
            key = (gds, i)
            if key in poly:

                if not isinstance(poly[key][0][0], np.ndarray):
                    raise TypeError("poly must be a 3D list")

                metals = tools.angusj(poly[key], poly[key], 'union')

                if i == 1:
                    metals = add_vias(gds, 1, datafield, poly, metals)
                elif i == 3:
                    metals = add_junctions(gds, 3, datafield, poly, metals)
                elif i == 7:
                    metals = add_ntrons(gds, 7, datafield, poly, metals)

                for pp in metals:
                    datafield.add(pp, key)


def mask(cell, datafield):
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

    myCell = gdsyuna.Cell('myCell')

    poly = cell.get_polygons(True)

    for key, layer in poly.items():
        cc_poly = list()

        for l1 in layer:
            if pyclipper.Orientation(l1) is False:
                reverse_poly = pyclipper.ReversePath(l1)
                cc_poly.append(reverse_poly)
            else:
                cc_poly.append(l1)

        union = tools.angusj(subj=cc_poly, method='union')
        upoly = pyclipper.CleanPolygons(union)

        if not isinstance(upoly[0][0], list):
            raise TypeError("poly must be a 3D list")

        create_mask(key, upoly, datafield, myCell)


def create_mask(key, union, datafield, myCell):

    named_layers = cl.defaultdict(dict)

    for l1 in union:
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

    # print('\n--- holes --------------')
    #
    # for hole in named_layers['holes']:
    #     print(hole)
    #
    # print('\n--- polygons --------------')
    #
    # for poly in named_layers['polygon']:
    #     print(poly)

    for poly in named_layers['polygon']:
        for hole in named_layers['holes']:
            if abs(hole.area) < abs(poly.area):

                ishole = True
                for point in hole.points:
                    if pyclipper.PointInPolygon(point, poly.points) != 1:
                        ishole = False

                if ishole:
                    datafield.add_mask(poly.points, key, hole.points)
                    myCell.add(gdsyuna.Polygon(hole.points, layer=81))
                else:
                    datafield.add_mask(poly.points, key)

        myCell.add(gdsyuna.Polygon(poly.points, key[0], verbose=False))
