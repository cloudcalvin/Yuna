import numpy as np
import networkx as nx
import itertools
import gdspy
import pyclipper

from yuna import utils
from yuna import devices

from .utils import logging

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from collections import namedtuple
from collections import defaultdict

from yuna import masternodes as mn
from yuna import cell_labels as cl

logger = logging.getLogger(__name__)


def add_cell_components(cell, datafield):
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
            cl.vias(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'jj':
            cl.junctions(subcell, datafield)

    for subcell in cell.get_dependencies(True):
        if subcell.name.split('_')[0] == 'ntron':
            cl.ntrons(subcell, datafield)


def update_datafield_labels(cell, datafield):
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

    utils.green_print('Processing LVS mask polygons')

    cell_layout = cell.copy('Polygon Flatten', deep_copy=True)
    cell_layout.flatten()

    poly = _etl_polygons(datafield, cell_layout)

    metals = defaultdict(dict)

    wires = {**datafield.pcd.layers['ix'],
             **datafield.pcd.layers['res']}

    for gds, layer in wires.items():
        if (gds, 0) in poly:
            metals[gds] = devices.Metal(gds, poly)

    for key, metal in metals.items():
        logging.info((key, metal))

    vias = defaultdict(dict)
    jjs = defaultdict(dict)
    ntrons = defaultdict(dict)

    for gds, layer in wires.items():
        if gds in metals:
            if (gds, 1) in poly:
                via = devices.Via(gds, poly)
                # via.update_mask(datafield)
                vias[gds] = via

            if (gds, 3) in poly:
                jj = devices.Junction(gds, poly)
                # jj.update_mask(datafield)
                jjs[gds] = jj

            if (gds, 7) in poly:
                ntron = devices.Ntron(gds, poly)
                # ntron.update_mask(datafield)
                ntrons[gds] = ntron

    # # TODO: We use a dict so that we can do individual unittests like this.
    # metals[6].add(vias[6])
    # metals[6].update_mask(datafield)

    for gds, metal in metals.items():
        if gds in vias:
            metal.add(vias[gds])

    for gds, metal in metals.items():
        if gds in jjs:
            metal.add(jjs[gds])

            jjs[gds].update_mask(datafield)
            # if gds in vias:
            #     via.update_mask(datafield, ntrons[gds])

    for gds, metal in metals.items():
        if gds in ntrons:
            metal.add(ntrons[gds])

            ntrons[gds].update_mask(datafield)
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
            metals[gds] = devices.Metal(gds, poly)
            metals[gds].create_mask(datafield, myCell)
