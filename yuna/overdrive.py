import os
import gdspy
import pyclipper

from yuna import process
from yuna import utils

from .utils import logging

import yuna.model as model
import yuna.lvs as lvs
import yuna.labels as labels
import yuna.masks as devices
import yuna.masternodes as mn

from yuna.lvs.geometry import Geometry

import pathlib


def _init_geom():
    geom = pygmsh.opencascade.Geometry(
        characteristic_length_min=0.1,
        characteristic_length_max=0.1,
    )

    geom.add_raw_code('Mesh.Algorithm = 100;')
    geom.add_raw_code('Coherence Mesh;')

    return geom


def _viewing(gdsii, geom):
    geom.parse_gdspy(gdspy.Cell('yuna_geom'))

    debug_dir = os.getcwd() + '/debug/'
    pathlib.Path(debug_dir).mkdir(parents=True, exist_ok=True)

    layout_file = debug_dir + 'yuna_geometry.gds'

    # gdspy.GdsLibrary(name='simplified_geometry')
    # # usercell = gdspy.Cell('yuna_geom')
    # usercell = gdsii.extract('yuna_geom')
    # 
    # 
    # cells = [usercell]
    # for cell in usercell.get_dependencies(True):
    #     cells.append(cell)

    # gdspy.write_gds(debug_dir + usercell.name + 'awe.gds',
    #                 cells,
    #                 name='simplified_geometry',
    #                 unit=1.0e-12)

    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-6)
    gdspy.LayoutViewer(cells='yuna_geom')


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


def grand_summon(gdsii, cell, pdk_file, basedir=None,
                 log=None, model=False, debug=None):
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

    utils.cyan_print('Summoning Yuna...')

    if log == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif log == 'info':
        logging.basicConfig(level=logging.INFO)

    if model is True:
        cell = _read_cell(gds_file, cell_name)
        # model.mask.geometry(cell, datafield)
        geom = Geometry(cell_name, pdk_file)

        utils.magenta_print('3D Model')

        pygmsh_geom = _init_geom()

        model.mask._metals(pygmsh_geom, geom)
        model.mask.terminals(pygmsh_geom, cell, geom)

        meshdata = pygmsh.generate_mesh(pygmsh_geom,
                                        verbose=False,
                                        geo_filename=modelname + '.geo')

        meshio.write(modelname + '.vtu', *meshdata)

        utils.end_print()
    else:
        geom = Geometry(cell.name, pdk_file)

        geom.user_label_term(cell)
        geom.user_label_cap(cell)

        geom.label_cells(cell)
        geom.label_flatten(cell)

        geom.deposition(cell)

        _pattern(geom)

        geom.update_polygons()

    if debug == 'view':
        _viewing(gdsii, geom)

    utils.cyan_print('Yuna. Done.\n')

    if geom is None:
        raise ValueError('datafield cannot be None')

    return geom
