"""

Usage:
    yuna <testname> <ldf> --cell=<cellname [--union] [--model=<modelname>]
    yuna <testname> --cell=<cellname [--debug=<debug>]
    yuna (-h | --help)
    yuna (-V | --version)

Options:
    -h --help     show this screen.
    -V --version  show version.
    --verbose     print more text

"""


import os
import meshio
import pygmsh
import gdspy
import pyclipper

from docopt import docopt

from yuna import process
from yuna import utils

from .utils import logging

import yuna.model as model
import yuna.lvs as lvs
import yuna.labels as labels
import yuna.masks as devices
import yuna.masternodes as mn

from yuna.masks.paths import Path
from yuna.masks.vias import Via
from yuna.masks.junctions import Junction
from yuna.masks.ntrons import Ntron

from yuna.lvs.geometry import Geometry


def _read_cell(gds_file, cell_name):
    gdsii = gdspy.GdsLibrary()

    gdsii.read_gds(gds_file, unit=1.0e-12)

    return gdsii.extract(cell_name)


def _init_geom():
    geom = pygmsh.opencascade.Geometry()

    geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
    geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

    geom.add_raw_code('Mesh.Algorithm = 100;')
    geom.add_raw_code('Coherence Mesh;')

    return geom


def _viewing(geom, debug):
    geom.parse_gdspy(gdspy.Cell('yuna_geom'))
    
    directory = os.getcwd() + '/debug/'
    layout_file = directory + 'yuna.gds'

    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-6)

    if debug == 'view':
        gdspy.LayoutViewer()


def _get_files(basedir, name):
    def _files(path):  
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                yield file

    gds_file, config_file = '', None

    for file in _files("."):  
        if file.endswith('.gds'):
            gds_file = basedir + '/' + file
        elif file.endswith('.json'):
            if file == name:
                config_file = basedir + '/' + file

    return gds_file, config_file


def grand_summon(basedir, cell_name, pdk_name, log=None, model=False, debug=None):
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
        Name of the cell inside the top-level gds layout that has
        to be executed.
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

    if not cell_name:
        raise ValueError('please specify a valid cell name')

    gds_file, config_file = _get_files(basedir, pdk_name)

    if model is True:
        # cell = read_cell(gds_file, cellname)
        # model.mask.geometry(cell, datafield)

        utils.magenta_print('3D Model')

        pygmsh_geom = _init_geom()

        model.mask._metals(pygmsh_geom, datafield)
        model.mask.terminals(pygmsh_geom, cell, datafield)

        meshdata = pygmsh.generate_mesh(pygmsh_geom,
                                        verbose=False,
                                        geo_filename=modelname + '.geo')

        meshio.write(modelname + '.vtu', *meshdata)

        utils.end_print()
    else:
        print(gds_file)

        cell = _read_cell(gds_file, cell_name)

        geom = Geometry(cell_name, config_file)

        geom.user_label_term(cell)
        geom.user_label_cap(cell)

        geom.label_cells(cell)
        geom.label_flatten(cell)

        geom.deposition(cell)

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

        geom.update_polygons()

    _viewing(geom, debug)

    utils.cyan_print('Yuna. Done.\n')

    return geom





