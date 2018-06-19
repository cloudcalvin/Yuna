import os
import gdspy
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

import pathlib


logger = logging.getLogger(__name__)


# def _get_dependencies(elements, recursive=False):
#     dependencies = {}
#     print(dependencies)

#     for element in elements:
#         if isinstance(element, gdspy.CellReference) or isinstance(
#                 element, gdspy.CellArray):
            
#             ref_cell = element.ref_cell

#             if recursive:
#                 dependencies.update(ref_cell.get_dependencies(elements, True))

#             if element.ref_cell in dependencies:
#                 dependencies[ref_cell].append(element.origin)
#             else:
#                 dependencies[ref_cell] = [element.origin]

#     return dependencies


from yuna.cell import Cell
from yuna.sref import SRef
from yuna.label import Label

from yuna.library import Library
from yuna.polygon import Polygon

import json


def _define_capacitor(library, topcell, cell_list):
    cap_cell = None
    for cell in topcell.get_dependencies(True):
        if cell.name == 'Capacitor':
            cap_cell = cell

    cap = Cell('Capacitor')

    for element in cap_cell.elements:
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name

            params = {}
            params['rotation'] = element.rotation
            params['magnification'] = element.magnification
            params['x_reflection'] = element.x_reflection

            cap += SRef(cell_list[name], element.origin, **params)
        elif isinstance(element, gdspy.Polygon):
            params = {}
            params['layer'] = element.layer
            params['datatype'] = element.datatype

            cap += Polygon(element.points, **params)
        elif isinstance(element, gdspy.PolygonSet):
            raise ValueError('Implement PolygonSet support')

    return cap


def _define_cshe(topcell, cell_list):
    cap_cell = None
    for cell in topcell.get_dependencies(True):
        if cell.name == 'CSHE':
            cap_cell = cell

    cap = Cell('CSHE')

    for element in cap_cell.elements:
        if isinstance(element, gdspy.CellReference):
            name = element.ref_cell.name

            params = {}
            params['rotation'] = element.rotation
            params['magnification'] = element.magnification
            params['x_reflection'] = element.x_reflection

            # if isinstance(cell_list[name], Cell.registry['Via']):
            cap += SRef(cell_list[name], element.origin, **params)
        elif isinstance(element, gdspy.Polygon):
            params = {}
            params['layer'] = element.layer
            params['datatype'] = element.datatype

            cap += Polygon(element.points, **params)
        elif isinstance(element, gdspy.PolygonSet):
            raise ValueError('Implement PolygonSet support')

    return cap


def user_label_cap(cell):
    caps = []
  
    pdk = get_pdk()

    for lbl in cell.labels:
        if lbl.text[0] == 'C':
            params = pdk['Structure']['Capacitor']
            # params['text'] = lbl.text
            params['layer'] = lbl.layer
            params['anchor'] = lbl.anchor
            params['rotation'] = lbl.rotation
            params['magnification'] = lbl.magnification
            params['x_reflection'] = lbl.x_reflection
            params['texttype'] = lbl.texttype
            params['ports'] = utils.calculate_ports(lbl.text.split(' '), pdk)

            Capacitor = type('Capacitor', (Label,), params)
            cap = Capacitor(lbl.text, lbl.position, **params)

            caps.append(cap)

    return caps


def user_label_term(cell):
    terms = []

    pdk = get_pdk()

    for lbl in cell.labels:
        if lbl.text[0] == 'P':
            params = pdk['Structure']['Terminal']['63']
            # params['text'] = lbl.text
            params['layer'] = lbl.layer
            params['anchor'] = lbl.anchor
            params['rotation'] = lbl.rotation
            params['magnification'] = lbl.magnification
            params['x_reflection'] = lbl.x_reflection
            params['texttype'] = lbl.texttype

            params['ports'] = utils.calculate_ports(lbl.text.split(' '), pdk)

            Terminal = type('Terminal', (Label,), params)
            term = Terminal(lbl.text, lbl.position, **params)

            terms.append(term)

    return terms


def element_center(element):
    bb = element.get_bounding_box()
    cx = ( (bb[0][0] + bb[1][0]) / 2.0 ) + 10.0
    cy = ( (bb[0][1] + bb[1][1]) / 2.0 )

    return (cx, cy)

    # lbl = gdspy.Label(name, (cx, cy), 0, layer=64)
    # cell.add(lbl)


def get_pdk():
    pdk = os.getcwd() + '/technology/' + 'raytheon.json'

    data = None
    with open(pdk) as data_file:
        data = json.load(data_file)
    return data


def grand_summon(topcell, pdk_file):
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

    # if log == 'debug':
    #     logging.basicConfig(level=logging.DEBUG)
    # elif log == 'info':
    #     logging.basicConfig(level=logging.INFO)

    library = Library(name='yuna_library')

    geom = Cell('Geometry')

    pdk = get_pdk()

    cell_list = {}
    for cell in topcell.get_dependencies(True):
        name = cell.name

        if name.startswith('via'):
            MyNode = type('Via', (Cell,), {})
            ccell = MyNode(name, cell=cell)
            ccell.flatten(single_datatype=1)

            for key, layer in pdk['Cells']['Vias'].items():
                if key != 'color' and key == name:
                    params = {}
                    params = layer

                    params['layer'] = 64
                    params['anchor'] = 'o'
                    params['rotation'] = None
                    params['magnification'] = None
                    params['x_reflection'] = False
                    params['texttype'] = 0

                    position = element_center(ccell)

                    MLabel = type('Via', (Label,), params)
                    cap_label = MLabel(name, position, **params)

                    ccell += cap_label

                    geom += cap_label
            
        elif name.startswith('ntron'):
            MyNode = type('Ntron', (Cell,), {})
            ccell = MyNode(name, cell=cell)
            ccell.flatten(single_datatype=7)

            for key, layer in pdk['Cells']['Vias'].items():
                if key != 'color' and key == name:
                    params = {}
                    params = layer

                    params['layer'] = 64
                    params['anchor'] = 'o'
                    params['rotation'] = None
                    params['magnification'] = None
                    params['x_reflection'] = False
                    params['texttype'] = 0

                    position = element_center(ccell)

                    MLabel = type('Via', (Label,), params)
                    cap_label = MLabel(name, position, **params)

                    ccell += cap_label

                    geom += cap_label

        else:
            MyNode = type('Normal', (Cell,), {})
            ccell = MyNode(name, cell=cell)

        cell_list[name] = ccell

    for element in topcell.elements:
        if isinstance(element, gdspy.CellReference):

            if element.ref_cell.name == 'Capacitor':
                cap = _define_capacitor(library, topcell, cell_list)

                library += cap

                geom += SRef(cap, element.origin)

            if element.ref_cell.name == 'CSHE':
                cshe = _define_cshe(topcell, cell_list)

                library += cshe

                geom += SRef(cshe, element.origin)

    caps = user_label_cap(topcell)
    terms = user_label_term(topcell)

    for cap in caps:
        geom += cap
    for term in terms:
        geom += term

    library += geom

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


# def _pattern_polygons(geom):
#     print('[*] Pattern polygons')

#     from yuna.masks.paths import Path
#     from yuna.masks.vias import Via
#     from yuna.masks.junctions import Junction
#     from yuna.masks.ntrons import Ntron

#     from yuna.masternode import MasterNode

#     MasterVia = MasterNode.registry['Via']
#     MasterNtron = MasterNode.registry['Ntron']
            
#     if geom.has_device(MasterVia):
#         geom.patterning(masktype=Path, devtype=Via)
#     if geom.has_device(MasterNtron):
#         geom.patterning(masktype=Path, devtype=Ntron)
#     if geom.has_device(mn.junction.Junction):
#         geom.patterning(masktype=Path, devtype=Junction)

#     if geom.has_device(MasterNtron):
#         geom.patterning(masktype=Via, devtype=Ntron)
#     if geom.has_device(mn.junction.Junction):
#         geom.patterning(masktype=Via, devtype=Junction)

#     geom.update()
#     geom.mask_polygons()


# def _constuct_polygons(geom, cell):
#     import collections as cl

#     cell_layout = cell.copy('Polygon Flatten',
#                             exclude_from_current=True,
#                             deep_copy=True)
#     cell_layout.flatten()

#     data = geom.raw_pdk_data['Layers']
#     params = [*data['ix'], *data['res']]

#     def _etl_polygons(params, cell):
#         """
#         Reads throught the PDF file and converts the corresponding
#         conducting layers to the same type. An example of this is
#         layer NbN_1 and NbN_2 that should be the same.

#         Output : dict()
#             Updated `poly` version that has converted the ETL polygons.
#         """

#         logger.info('ETL Polygons')

#         pp = cell.get_polygons(True)

#         ply = cl.defaultdict(list)

#         for ll in params:
#             if 'ETL' in ll:
#                 p = {(ll['ETL'], k[1]): v for k, v in pp.items() if ll['layer'] == k[0]}
#             else:
#                 p = {k: v for k, v in pp.items() if ll['layer'] == k[0]}

#             for k, v in p.items():
#                 ply[k].extend(v)
#         return ply

#     mask_poly = _etl_polygons(params, cell_layout)

#     geom.deposition(mask_poly, params=params)


# def _labels_flat(geom, cell):
#     print('[*] Flatten cell labels')

#     sumlabel.cells(geom, cell)

#     cl = cell.copy('Label Flatten',
#                    exclude_from_current=True,
#                    deep_copy=True)

#     cell_labels = cl.flatten().get_labels(0)

#     if len(cell_labels) > 0:
#         for label in cell_labels:
#             logging.info(label.text)

#     sumlabel.devices(geom, cell_labels)
#     # geom.label_flatten(cell_labels)


# # def _add_labels(geom, cell):

# #     for subcell in cell.get_dependencies(True):
# #         if subcell.name.split('_')[0] == 'via':
# #             cc = sumlabel.CheckCell('via', 1)

# #             cc.add_pin_label(subcell)

# #             # labels.cell.vias(subcell, geom)

# #     # def label_cells(cell, ):
# #     #     for subcell in cell.get_dependencies(True):
# #     #         if subcell.name.split('_')[0] == 'via':
# #     #             labels.cell.vias(subcell, geom)

# #     # class Via(CellLabel):
# #     #     name = cell.name
# #     #     ltype = 'via'
# #     #     datatype = 1
# #     #     element = cell

# #     # class Ntron(CellLabel):
# #     #     name = cell.name
# #     #     ltype = 'ntron'
# #     #     datatype = 7
# #     #     element = cell

# #     # v = CellLabel(geom, cell, ltype='via', datatype=1)
# #     # v = CellLabel(geom, cell, ltype='ntron', datatype=7)


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
