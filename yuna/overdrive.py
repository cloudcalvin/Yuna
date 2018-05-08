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
from yuna import model
from yuna import deck

from .datafield import DataField

from yuna import user_labels as ul
from yuna import polygons

from .utils import logging


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


def read_cell(gds_file, cellname):
    gdsii = gdspy.GdsLibrary()

    gdsii.read_gds(gds_file, unit=1.0e-12)

    # all_cells = gdsii.extract('Array_4x4').get_dependencies(True)
    #
    # for cell in all_cells:
    #     # print(cellname)
    #     print(cell.name)
    #     if cell.name == cellname:
    #         return cell

    return gdsii.extract(cellname)


def init_geom():
    geom = pygmsh.opencascade.Geometry()

    geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
    geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

    geom.add_raw_code('Mesh.Algorithm = 100;')
    geom.add_raw_code('Coherence Mesh;')

    return geom


def viewing(datafield):
    datafield.parse_gdspy(gdspy.Cell('View Cell Test'))

    gdspy.LayoutViewer()

    gdspy.write_gds('ex_layout.gds', unit=1.0e-6, precision=1.0e-6)


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
    config_name = args['<configname>']
    cwd = ''

    if args['--logging'] == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif args['--logging'] == 'info':
        logging.basicConfig(level=logging.INFO)

    if not cellname:
        raise ValueError('please specify a valid cell name')

    gds_file, config_file = '', None
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.gds'):
                gds_file = basedir + '/' + file
            elif file.endswith('.json'):
                if file == config_name:
                    config_file = basedir + '/' + file

    cell = read_cell(gds_file, cellname)

    datafield = DataField('Hypres', config_file)

    deck.model_mask(cell, datafield)

    ul.terminals(cell, datafield)
    ul.capacitors(cell, datafield)

    deck.add_cell_components(cell, datafield)
    deck.update_datafield_labels(cell, datafield)

    deck.lvs_mask(cell, datafield)

    # test_union()
    # test_all()

    if args['--model']:
        utils.magenta_print('3D Model')

        geom = init_geom()

        model.metals(geom, datafield)
        model.terminals(geom, cell, datafield)

        meshdata = pygmsh.generate_mesh(geom,
                                        verbose=False,
                                        geo_filename=modelname + '.geo')

        meshio.write(modelname + '.vtu', *meshdata)

        utils.end_print()

    viewing(datafield)

    utils.cyan_print('Yuna. Done.\n')

    return datafield
