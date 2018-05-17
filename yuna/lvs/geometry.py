import numpy as np
import networkx as nx
import itertools
import gdspy
import pyclipper

from yuna import utils

from yuna.utils import logging
from yuna.utils import datatype

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from collections import namedtuple
from collections import defaultdict

import yuna.devices as devices
import yuna.labels as labels

from . import masternodes as mn
from yuna.utils import nm

logger = logging.getLogger(__name__)


def label_cells(cell, datafield):
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
            labels.cell.vias(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'jj':
            labels.cell.junctions(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'ntron':
            labels.cell.ntrons(subcell, datafield)


def label_flatten(cell, datafield):
    """
    Place the labels to their corresponding positions
    after flattening the top-level cell. Update the
    datafield object to include all labels in the layout.
    """

    utils.green_print('Place labels in flattened layout')

    cl = cell.copy('Label Flatten', deep_copy=True)

    cell_labels = cl.flatten().get_labels(0)

    if len(cell_labels) > 0:
        for label in cell_labels:
            logging.info(label.text)

    for lbl in cell_labels:
        comp = lbl.text.split('_')[0]

        if comp == 'via':
            via = mn.Via(lbl.text,
                         lbl.position,
                         atom=datafield.pcd.atoms['vias'])

            datafield.labels.append(via)

        if comp == 'jj':
            jj = mn.Junction(lbl.text,
                             lbl.position,
                             atom=datafield.pcd.atoms['jjs'])

            datafield.labels.append(jj)

        if comp == 'ntron':
            ntron = mn.Ntron(lbl.text,
                             lbl.position,
                             atom=datafield.pcd.atoms['ntrons'])

            datafield.labels.append(ntron)

        if comp == 'shunt':
            shunt = mn.Shunt(lbl.text,
                             lbl.position,
                             atom=datafield.pcd.atoms['jjs'])

            datafield.labels.append(shunt)

        if comp == 'ground':
            ground = mn.Ground(lbl.text,
                               lbl.position,
                               atom=datafield.pcd.atoms['jjs'])

            datafield.labels.append(ground)


def _etl_polygons(datafield, cell):
    """
    Reads throught the PDF file and converts the corresponding
    conducting layers to the same type. An example of this is
    layer NbN_1 and NbN_2 that should be the same.

    Output : dict()
        Updated `poly` version that has converted the ETL polygons.
    """

    logger.info('ETL Polygons')

    poly = cell.get_polygons(True)

    polygons = dict()

    wires = {**datafield.pcd.layers['ix'],
             **datafield.pcd.layers['res']}

    for gds, layer in wires.items():
        if layer.etl is not None:
            for key, points in poly.items():
                if gds == key[0]:
                    etl_key = (layer.etl, key[1])
                    for pp in points:
                        if etl_key in polygons:
                            polygons[etl_key].append(pp)
                        else:
                            polygons[etl_key] = [pp]
        else:
            for key, points in poly.items():
                if gds == key[0]:
                    for pp in points:
                        if key in polygons:
                            polygons[key].append(pp)
                        else:
                            polygons[key] = [pp]
    return polygons


def deposition(cell, datafield):
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

    mask_poly = _etl_polygons(datafield, cell_layout)

    wires = {**datafield.pcd.layers['ix'],
             **datafield.pcd.layers['res']}

    # Mask = namedtuple('Mask', ['dtype', 'devices'])

    # paths = Mask(dtype=datatype['path'], element=[])
    # vias = Mask(dtype=datatype['via'], element=[])
    # jjs = Mask(dtype=datatype['jj'], element=[])
    # ntrons = Mask(dtype=datatype['ntron'], element=[])

    for gds, layer in wires.items():
        if (gds, datatype['path']) in mask_poly:
            path = devices.paths.Paths(gds, datafield.pcd, mask_poly)
            datafield.add_mask(gds, path)

            if (gds, datatype['via']) in mask_poly:
                via = devices.vias.Via(gds, mask_poly)
                datafield.add_mask(gds, via)

            if (gds, datatype['jj']) in mask_poly:
                jj = devices.junctions.Junction(gds, mask_poly)
                datafield.add_mask(gds, jj)

            if (gds, datatype['ntron']) in mask_poly:
                ntron = devices.ntrons.Ntron(gds, mask_poly)
                datafield.add_mask(gds, ntron)

    datafield.pattern_path(devices.vias.Via)
    datafield.pattern_path(devices.ntrons.Ntron)
    datafield.pattern_path(devices.junctions.Junction)

    datafield.pattern_via(devices.ntrons.Ntron)
    datafield.pattern_via(devices.junctions.Junction)

    datafield.update_polygons()
