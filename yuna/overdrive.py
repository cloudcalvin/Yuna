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


def _pattern(geom):
    from yuna.masks.paths import Path
    from yuna.masks.vias import Via
    from yuna.masks.junctions import Junction
    from yuna.masks.ntrons import Ntron

    if geom.has_device(mn.via.Via):
        geom.patterning(masktype=Path, devtype=Via)
    if geom.has_device(mn.ntron.Ntron):
        geom.patterning(masktype=Path, devtype=Ntron)
    if geom.has_device(mn.junction.Junction):
        geom.patterning(masktype=Path, devtype=Junction)

    if geom.has_device(mn.ntron.Ntron):
        geom.patterning(masktype=Via, devtype=Ntron)
    if geom.has_device(mn.junction.Junction):
        geom.patterning(masktype=Via, devtype=Junction)

    geom.update()
    geom.mask_polygons()


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
    geom.label_flatten(cell)

    geom.deposition(cell)

    _pattern(geom)

    _write_gds(gdsii, geom, viewer)

    if geom is None:
        raise ValueError('datafield cannot be None')

    utils.cyan_print('Yuna. Done.\n')

    return geom
