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

import yuna.masks as devices
import yuna.labels as labels

from yuna.masternodes.via import Via
from yuna.masternodes.junction import Junction
from yuna.masternodes.junction import Shunt
from yuna.masternodes.junction import Ground
from yuna.masternodes.ntron import Ntron

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
            via = Via(lbl.text,
                         lbl.position,
                         atom=datafield.pcd.atoms['vias'])

            datafield.labels.append(via)

        if comp == 'jj':
            jj = Junction(lbl.text,
                             lbl.position,
                             atom=datafield.pcd.atoms['jjs'])

            datafield.labels.append(jj)

        if comp == 'ntron':
            ntron = Ntron(lbl.text,
                             lbl.position,
                             atom=datafield.pcd.atoms['ntrons'])

            datafield.labels.append(ntron)

        if comp == 'shunt':
            shunt = Shunt(lbl.text,
                             lbl.position,
                             atom=datafield.pcd.atoms['jjs'])

            datafield.labels.append(shunt)

        if comp == 'ground':
            ground = Ground(lbl.text,
                               lbl.position,
                               atom=datafield.pcd.atoms['jjs'])

            datafield.labels.append(ground)
