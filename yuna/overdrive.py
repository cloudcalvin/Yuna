import os
import json
import gdspy
import pathlib
import pyclipper

from yuna import process
from yuna import utils
import yuna.summon.label as sumlabel

from .utils import logging

import yuna.lvs as lvs
import yuna.labels as labels
import yuna.masks as devices
import yuna.masternodes as mn

from yuna.lvs.geometry import Geometry

from yuna.cell import Cell
from yuna.sref import SRef
from yuna.label import Label

from yuna.library import Library
from yuna.polygon import Polygon

from yuna.lvs_extract import *
from yuna.read_pdk import *


logger = logging.getLogger(__name__)


def grand_summon(topcell, pdk_file, json_devices=[]):
    """
    Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh.

    Parameters
    ----------
    basedir : string
        Current working directory string.
    args : docopt library object
        Contains the args received from ExVerify

    Arguments
    ---------
    cell : string
        Name of the cell inside the top-level gds layout
        that has to be executed.
    config_name : string
        Name of the process configuration file.
    model : bool
        If True then a 3D model of the cell must be created.
    """

    print('---------- Yuna ----------\n')

    library = Library(name='Yuna Library')

    structure = Cell('Structure')

    pdk = get_pdk()

    print('-------------------- ** AUTO LABELS ** --------------------\n')

    cell_list = create_device_cells(topcell, json_devices)

    sref_list = convert_to_yuna_cells(library, topcell, cell_list)

    for sref in sref_list:
        structure += sref

    print('-------------------- ** USER LABELS ** --------------------\n')

    class_name = 'Capacitor'
    params = pdk['Structure'][class_name]
    caps = user_label(class_name, 'C', topcell, params)

    class_name = 'Terminal'
    params = pdk['Structure'][class_name]['63']
    terms = user_label(class_name, 'P', topcell, params)

    for cap in caps:
        structure += cap
    for term in terms:
        structure += term

    structure.flat_copy(duplicate_layer={4: 5})

    # TODO: Update this functions.
    structure.update_labels(oktypes=['Via', 'Ntron'])

    print('-------------------- ** POLYGONS ** --------------------\n')

    pdk_layers = [*pdk['Layers']['ix'], *pdk['Layers']['via']]

    devices = dynamic_cells(json_devices)

    for key, value in structure.get_polygons(True).items():
        for name, device in devices.items():
            mask_levels(key, device, value, pdk_layers)

    devices['Path'].cell - devices['Via'].cell
    devices['Path'].cell - devices['Ntron'].cell
    devices['Via'].cell - devices['Ntron'].cell

    geom = Cell('Geometry')

    geom += SRef(devices['Path'].cell, (0, 0))
    geom += SRef(devices['Via'].cell, (0, 0))
    geom += SRef(devices['Ntron'].cell, (0, 0))

    geom.flat_copy()

    print('-------------------- ** FINAL ** --------------------\n')

    library += structure
    library += geom

    for name, device in devices.items():
        library += device.cell

    geom.view(library)

    # --------------------------- END ------------------------------ #

    # library.view()
    # library.write()

    if geom is None:
        raise ValueError('Geometry field cannot be None')

    utils.cyan_print('\n----- Yuna. Done. -----\n')

    return geom
