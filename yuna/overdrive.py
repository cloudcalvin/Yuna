import os
import gdspy
import pyclipper

from yuna import process
from yuna import utils

from .utils import logging

import yuna.lvs as lvs
import yuna.labels as labels
import yuna.masks as devices
import yuna.masternodes as mn

from yuna.lvs.geometry import Geometry

import pathlib


logger = logging.getLogger(__name__)


def _write_gds(gdsii, geom, viewer):
    auron_cell = gdspy.Cell('geom_for_auron')
    ix_cell = gdspy.Cell('geom_for_inductex')

    geom.gds_auron(auron_cell)
    geom.gds_inductex(ix_cell)

    debug_dir = os.getcwd() + '/debug/'
    pathlib.Path(debug_dir).mkdir(parents=True, exist_ok=True)

    gdspy.GdsLibrary(name='auron_geom')
    gdspy.write_gds(debug_dir + 'auron.gds',
                    [auron_cell],
                    name='auron_geom',
                    unit=1.0e-12)

    gdspy.GdsLibrary(name='ix_geom')
    gdspy.write_gds(debug_dir + 'ix.gds',
                    [ix_cell],
                    name='ix_geom',
                    unit=1.0e-12)

    gdspy.write_gds(debug_dir + 'all_cells.gds',
                    unit=1.0e-12)

    if viewer == 'ix':
        gdspy.LayoutViewer(cells='geom_for_inductex')
    elif viewer == 'auron':
        gdspy.LayoutViewer(cells='geom_for_auron')
    elif viewer == 'all':
        gdspy.LayoutViewer()


def _pattern_polygons(geom):
    from yuna.masks.paths import Path
    from yuna.masks.vias import Via
    from yuna.masks.junctions import Junction
    from yuna.masks.ntrons import Ntron

    from yuna.masternode import MasterNode

    MasterVia = MasterNode.registry['Via']
    MasterNtron = MasterNode.registry['Ntron']
            
    if geom.has_device(MasterVia):
        geom.patterning(masktype=Path, devtype=Via)
    if geom.has_device(MasterNtron):
        geom.patterning(masktype=Path, devtype=Ntron)
    if geom.has_device(mn.junction.Junction):
        geom.patterning(masktype=Path, devtype=Junction)

    if geom.has_device(MasterNtron):
        geom.patterning(masktype=Via, devtype=Ntron)
    if geom.has_device(mn.junction.Junction):
        geom.patterning(masktype=Via, devtype=Junction)

    geom.update()
    geom.mask_polygons()


def _constuct_polygons(geom, cell):
    import collections as cl

    cell_layout = cell.copy('Polygon Flatten',
                            exclude_from_current=True,
                            deep_copy=True)
    cell_layout.flatten()

    data = geom.raw_pdk_data['Layers']
    params = [*data['ix'], *data['res']]

    def _etl_polygons(params, cell):
        """
        Reads throught the PDF file and converts the corresponding
        conducting layers to the same type. An example of this is
        layer NbN_1 and NbN_2 that should be the same.

        Output : dict()
            Updated `poly` version that has converted the ETL polygons.
        """

        logger.info('ETL Polygons')

        pp = cell.get_polygons(True)

        ply = cl.defaultdict(list)

        for ll in params:
            if 'ETL' in ll:
                p = {(ll['ETL'], k[1]): v for k, v in pp.items() if ll['layer'] == k[0]}
            else:
                p = {k: v for k, v in pp.items() if ll['layer'] == k[0]}

            for k, v in p.items():
                ply[k].extend(v)
        return ply

    mask_poly = _etl_polygons(params, cell_layout)

    geom.deposition(mask_poly, params=params)


def _labels_flat(geom, cell):
    cl = cell.copy('Label Flatten',
                   exclude_from_current=True,
                   deep_copy=True)

    cell_labels = cl.flatten().get_labels(0)

    if len(cell_labels) > 0:
        for label in cell_labels:
            logging.info(label.text)

    geom.label_flatten(cell_labels)


def grand_summon(gdsii, cell, pdk_file, log=None, viewer=None):
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

    print('----- Yuna -----\n')

    if log == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif log == 'info':
        logging.basicConfig(level=logging.INFO)

    geom = Geometry(cell, pdk_file)

    geom.user_label_term(cell)
    geom.user_label_cap(cell)

    geom.label_cells(cell)

    _labels_flat(geom, cell)

    _constuct_polygons(geom, cell)

    _pattern_polygons(geom)

    _write_gds(gdsii, geom, viewer)

    if geom is None:
        raise ValueError('datafield cannot be None')

    utils.cyan_print('\n----- Yuna. Done. -----\n')

    return geom
