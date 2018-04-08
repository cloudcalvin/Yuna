import gdspy
import pygmsh
import meshio
import numpy as np
import pyclipper

from yuna import utils
from collections import namedtuple

from .terminal import Terminal
from .metals import Metal
from .utils import um


def metals(geom, datafield):
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
