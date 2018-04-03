"""

Usage:
    yuna <process> <testname> <ldf> [--cell=<cellname>] [--union] [--model]
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
import gdsyuna

from docopt import docopt

from yuna import process
from yuna import tools
from yuna import modeling
from yuna import deck

from .datafield import DataField


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

    tools.cyan_print('Summoning Yuna...')

    cellname = args['--cell']
    config_name = args['<configname>']
    model = args['--model']
    cwd = ''

    if not cellname:
        raise ValueError('please specify a valid cell name')

    gds_file, config_file = '', ''
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.gds'):
                gds_file = basedir + '/' + file
            elif file.endswith('.json'):
                if file == config_name:
                    config_file = basedir + '/' + file

    gdsii = gdsyuna.GdsLibrary()
    gdsii.read_gds(gds_file, unit=1.0e-12)
    cell = gdsii.extract(cellname)

    cell_origin = cell.copy('Original', deep_copy=True)
    cell_origin.flatten()

    datafield = DataField('Hypres', config_file)

    deck.components(cell, datafield)
    deck.layers(cell, datafield)
    deck.mask(cell_origin, datafield)

    datafield.parse_gdspy(gdsyuna.Cell('View Cell Test'))

    # test_union()
    # test_all()

    if model is True:
        geom = pygmsh.opencascade.Geometry()

        geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
        geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

        geom.add_raw_code('Mesh.Algorithm = 100;')
        geom.add_raw_code('Coherence Mesh;')

        extruded = dict()

        # TODO: Fix the nTron fuckup.
        mask_layers = {**datafield.pcd.layers['ix'],
                       **datafield.pcd.layers['res'],
                       **datafield.pcd.layers['term'],
                       **datafield.pcd.layers['via'],
                       **datafield.pcd.layers['jj']}

        for gds, layer in mask_layers.items():
            modeling.wirechain(geom, gds, layer, datafield, extruded)

        # tc = modeling.terminals(wc, geom, config, configdata)

        meshdata = pygmsh.generate_mesh(geom, verbose=False, geo_filename='3D.geo')
        meshio.write('3D.vtu', *meshdata)

        tools.cyan_print('3D modeling setup finished\n')

    gdsyuna.LayoutViewer()
    gdsyuna.write_gds('auron.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.\n')

    return datafield
