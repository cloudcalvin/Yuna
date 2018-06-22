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
# from yuna.mask_polygon import MaskPolygon

from yuna.lvs_extraction import *


logger = logging.getLogger(__name__)


# def _define_capacitor(library, topcell, cell_list):
#     cap_cell = None
#     for cell in topcell.get_dependencies(True):
#         if cell.name == 'Capacitor':
#             cap_cell = cell

#     cap = Cell('Capacitor')

#     for element in cap_cell.elements:
#         if isinstance(element, gdspy.CellReference):
#             name = element.ref_cell.name

#             params = {}
#             params['rotation'] = element.rotation
#             params['magnification'] = element.magnification
#             params['x_reflection'] = element.x_reflection

#             cap += SRef(cell_list[name], element.origin, **params)
#         elif isinstance(element, gdspy.Polygon):
#             params = {}
#             params['layer'] = element.layer
#             params['datatype'] = element.datatype

#             cap += Polygon(element.points, **params)
#         elif isinstance(element, gdspy.PolygonSet):
#             raise ValueError('Implement PolygonSet support')

#     return cap


# def _define_cshe(topcell, cell_list):
#     cap_cell = None
#     for cell in topcell.get_dependencies(True):
#         if cell.name == 'CSHE':
#             cap_cell = cell

#     cap = Cell('CSHE')

#     for element in cap_cell.elements:
#         if isinstance(element, gdspy.CellReference):
#             name = element.ref_cell.name

#             params = {}
#             params['rotation'] = element.rotation
#             params['magnification'] = element.magnification
#             params['x_reflection'] = element.x_reflection

#             # if isinstance(cell_list[name], Cell.registry['Via']):
#             cap += SRef(cell_list[name], element.origin, **params)
#         elif isinstance(element, gdspy.Polygon):
#             params = {}
#             params['layer'] = element.layer
#             params['datatype'] = element.datatype

#             cap += Polygon(element.points, **params)
#         elif isinstance(element, gdspy.PolygonSet):
#             raise ValueError('Implement PolygonSet support')

#     return cap


# def user_label_cap(cell):
#     caps = []

#     pdk = get_pdk()

#     for lbl in cell.labels:
#         if lbl.text[0] == 'C':
#             params = pdk['Structure']['Capacitor']

#             params['text'] = lbl.text
#             params['layer'] = lbl.layer
#             params['anchor'] = lbl.anchor
#             params['rotation'] = lbl.rotation
#             params['magnification'] = lbl.magnification
#             params['x_reflection'] = lbl.x_reflection
#             params['texttype'] = lbl.texttype
#             params['ports'] = utils.calculate_ports(lbl.text.split(' '), pdk)

#             Capacitor = type('Capacitor', (Label,), params)
#             cap = Capacitor(lbl.position, **params)

#             caps.append(cap)

#     return caps


# def user_label_term(cell):
#     terms = []

#     pdk = get_pdk()

#     for lbl in cell.labels:
#         if lbl.text[0] == 'P':
#             params = pdk['Structure']['Terminal']['63']

#             params['text'] = lbl.text
#             params['layer'] = lbl.layer
#             params['anchor'] = lbl.anchor
#             params['rotation'] = lbl.rotation
#             params['magnification'] = lbl.magnification
#             params['x_reflection'] = lbl.x_reflection
#             params['texttype'] = lbl.texttype

#             params['ports'] = utils.calculate_ports(lbl.text.split(' '), pdk)

#             Terminal = type('Terminal', (Label,), params)
#             term = Terminal(lbl.position, **params)

#             terms.append(term)

#     return terms


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

    library = Library(name='yuna_library')

    geom = Cell('Geometry')

    pdk = get_pdk()

    print('-------------------- ** LABELS ** --------------------\n')

    cell_list = create_device_cells(topcell, json_devices)

    sref_list = convert_to_yuna_cells(library, topcell, cell_list)

    for sref in sref_list:
        geom += sref

    class_name = 'Capacitor'
    params = pdk['Structure'][class_name]
    caps = user_label(class_name, 'C', topcell, params)

    class_name = 'Terminal'
    params = pdk['Structure'][class_name]['63']
    terms = user_label(class_name, 'P', topcell, params)

    for cap in caps:
        geom += cap
    for term in terms:
        geom += term

    geom.flat_copy(duplicate_layer={4: 5})

    # TODO: Update this functions.
    geom.update_labels(oktypes=['Via', 'Ntron'])

    print('-------------------- ** POLYGONS ** --------------------\n')

    pdk_layers = [*pdk['Layers']['ix'], *pdk['Layers']['via']]

    pattern = Cell('Patterning')

    devices = dynamic_cells(json_devices)

    for key, value in geom.get_polygons(True).items():
        for name, device in devices.items():
            mask_levels(key, device, value, pdk_layers)

    devices['Path'].cell - devices['Via'].cell
    devices['Path'].cell - devices['Ntron'].cell
    devices['Via'].cell - devices['Ntron'].cell

    pattern += SRef(devices['Path'].cell, (0, 0))
    pattern += SRef(devices['Via'].cell, (0, 0))
    pattern += SRef(devices['Ntron'].cell, (0, 0))

    pattern.flat_copy()

    print('-------------------- ** FINAL ** --------------------\n')

    library += geom
    library += pattern

    print(devices)

    for name, device in devices.items():
        library += device.cell

    geom.view(library)

    # ------------------------- Old Yuna ---------------------------- #

    # geom = Geometry(cell, pdk_file)

    # ----- LABELS ----- #
    # geom.user_label_term(cell)
    # geom.user_label_cap(cel)
    # # _labels_flat(geom, cell)
    # _add_labels(geom, cell)

    # ----- POLYGONS ----- #
    # _constuct_polygons(geom, cell)
    # _pattern_polygons(geom)
    # _write_gds(gdsii, geom, viewer)

    # --------------------------- END ------------------------------ #

    if geom is None:
        raise ValueError('Geometry field cannot be None')

    utils.cyan_print('\n----- Yuna. Done. -----\n')

    return geom


# def _write_gds(gdsii, geom, viewer):
#     auron_cell = gdspy.Cell('geom_for_auron')
#     ix_cell = gdspy.Cell('geom_for_inductex')

#     geom.gds_auron(auron_cell)
#     geom.gds_inductex(ix_cell)

#     debug_dir = os.getcwd() + '/debug/'
#     pathlib.Path(debug_dir).mkdir(parents=True, exist_ok=True)

#     gdspy.GdsLibrary(name='auron_geom')
#     gdspy.write_gds(debug_dir + 'auron.gds',
#                     [auron_cell],
#                     name='auron_geom',
#                     unit=1.0e-12)

#     gdspy.GdsLibrary(name='ix_geom')
#     gdspy.write_gds(debug_dir + 'ix.gds',
#                     [ix_cell],
#                     name='ix_geom',
#                     unit=1.0e-12)

#     gdspy.write_gds(debug_dir + 'all_cells.gds',
#                     unit=1.0e-12)

#     if viewer == 'ix':
#         gdspy.LayoutViewer(cells='geom_for_inductex')
#     elif viewer == 'auron':
#         gdspy.LayoutViewer(cells='geom_for_auron')
#     elif viewer == 'all':
#         gdspy.LayoutViewer()
#     print('----- Yuna -----\n')
