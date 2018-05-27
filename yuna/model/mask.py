import gdspy
import numpy as np
import pyclipper

import yuna.utils as utils
from collections import namedtuple
from collections import defaultdict

from .terminal import Terminal
from .metals import Metal
from yuna.utils import um


def geometry(cell, datafield):
    """
    The layer polygons for each gdsnumber is created in four phases:

    0. Merge all the normal conducting wires.
    1. Merge the polygons inside each component.
    2. Find the difference between the conducting polygons
       and the component polygons.
    3. Add these polygons to the datafield object.

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
        if (gds, -1) in poly:
            metals[gds] = devices.Metal(gds, poly)
            metals[gds].create_mask(datafield, myCell)


def _metals(geom, datafield):
    metals = dict()

    # TODO: Fix the nTron fuckup.
    mask_layers = {**datafield.pcd.layers['ix'],
                   **datafield.pcd.layers['res'],
                   **datafield.pcd.layers['via'],
                   **datafield.pcd.layers['jj']}

    for gds, layer in mask_layers.items():
        if gds in datafield.mask:
            # TODO: Fix this hardcode
            if gds in [21, 6, 1]:
                for datatype, polygons in datafield.mask[gds].items():
                    for poly in polygons:
                        metals[gds] = Metal(poly)

                        metals[gds].set_surface(geom)
                        metals[gds].extrude(geom)


def terminals(geom, cell, datafield):
    terms = dict()

    for key, polygons in datafield.get_terminals().items():
        for points in polygons:
            for lbl in cell.labels:
                if pyclipper.PointInPolygon(lbl.position, points) == 1:
                    print('     .terms detected: ' + lbl.text)
                    terms[lbl.text] = Terminal([points])

    for name, term in terms.items():
        term.set_slope()
        term.metal_connection(datafield, name)
        term.metal_edge(datafield)
        term.extrude(geom, datafield)

    utils.write_cell((99, 0), 'Terminal Edges', terms)
