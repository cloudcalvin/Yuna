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


# def test_all():
#     geom = pygmsh.opencascade.Geometry(
#         characteristic_length_min=0.1,
#         characteristic_length_max=0.1,
#         )
#
#     rectangle = geom.add_rectangle([-1.0, -1.0, 0.0], 2.0, 2.0)
#     disk1 = geom.add_disk([-1.0, 0.0, 0.0], 0.5)
#     disk2 = geom.add_disk([+1.0, 0.0, 0.0], 0.5)
#     union = geom.boolean_union([rectangle, disk1, disk2])
#
#     disk3 = geom.add_disk([0.0, -1.0, 0.0], 0.5)
#     disk4 = geom.add_disk([0.0, +1.0, 0.0], 0.5)
#     geom.boolean_difference([union], [disk3, disk4])
#
#     ref = 4.0
#     union = pygmsh.generate_mesh(geom, geo_filename='differnce.geo')
#
#
# def test_union():
#     geom = pygmsh.opencascade.Geometry(
#         characteristic_length_min=0.1,
#         characteristic_length_max=0.1,
#         )
#
#     rectangle = geom.add_rectangle([-1.0, -1.0, 0.0], 2.0, 2.0)
#     disk_w = geom.add_disk([-1.0, 0.0, 0.0], 0.5)
#     disk_e = geom.add_disk([+1.0, 0.0, 0.0], 0.5)
#
#     frags = geom.boolean_fragments([rectangle], [disk_w, disk_e])
#
#     union = pygmsh.generate_mesh(geom, geo_filename='union.geo')


def _read_cell(gds_file, cellname):
    gdsii = gdspy.GdsLibrary()

    gdsii.read_gds(gds_file, unit=1.0e-12)

    return gdsii.extract(cellname)


def _init_geom():
    geom = pygmsh.opencascade.Geometry()

    geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
    geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

    geom.add_raw_code('Mesh.Algorithm = 100;')
    geom.add_raw_code('Coherence Mesh;')

    return geom


def _viewing(datafield):
    datafield.parse_gdspy(gdspy.Cell('View Cell Test'))

    gdspy.LayoutViewer()

    gdspy.write_gds('ex_layout.gds', unit=1.0e-6, precision=1.0e-6)


def _get_files(basedir, name):
    gds_file, config_file = '', None
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.gds'):
                gds_file = basedir + '/' + file
            elif file.endswith('.json'):
                if file == name:
                    config_file = basedir + '/' + file
    return gds_file, config_file


def grand_summon(basedir, args):
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

    cellname = args['--cell']
    pdk_name = args['<pdkname>']

    if args['--logging'] == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif args['--logging'] == 'info':
        logging.basicConfig(level=logging.INFO)

    if not cellname:
        raise ValueError('please specify a valid cell name')

    gds_file, config_file = _get_files(basedir, pdk_name)

    # test_union()
    # test_all()

    if args['--model']:
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
        cell = _read_cell(gds_file, cellname)

        geom = lvs.datafield.DataField('Hypres', config_file)

        labels.user.terminals(cell, geom)
        labels.user.capacitors(cell, geom)

        lvs.geometry.label_cells(cell, geom)
        lvs.geometry.label_flatten(cell, geom)

        geom.deposition(cell)

        geom.pattern_path(devices.vias.Via)
        geom.pattern_path(devices.ntrons.Ntron)
        geom.pattern_path(devices.junctions.Junction)

        geom.pattern_via(devices.ntrons.Ntron)
        geom.pattern_via(devices.junctions.Junction)

        geom.update_polygons()

    _viewing(geom)

    utils.cyan_print('Yuna. Done.\n')

    return geom
