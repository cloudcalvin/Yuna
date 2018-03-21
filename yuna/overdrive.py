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
import json
import meshio
import pygmsh
import gdsyuna
import numpy as np

from docopt import docopt

from yuna import process
from yuna import tools
from yuna import modeling

from .datafield import DataField


def update_wirechain(geom, key, poly_list, wirechain, datafield):
    """

    """

    gds = key[0]
    datatype = key[1]

    for i, poly1 in enumerate(poly_list):
        for j, poly2 in enumerate(poly1.get_points()):
            for points in poly2:
                polyname = str(gds) + '_' + str(datatype) + '_' + str(j+i)
                gp = geom.add_polygon(points, lcar=0.1, make_surface=True)
                geom.add_physical_surface(gp.surface, label=polyname)

                if gds in wirechain:
                    wirechain[gds].append(gp.surface)
                else:
                    wirechain[gds] = [gp.surface]

    # meshio.write('3d_model.vtk', *layer_mesh)


def gmsh_wirechain(datafield):
    wires = {**datafield.pcd.layers['ix'], **datafield.pcd.layers['res']}

    for gds in wires.keys():
        geom = pygmsh.opencascade.Geometry()

        geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
        geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

        wirechain = {}

        for datatype, poly_list in datafield.polygons[gds].items():
            key = (gds, datatype)
            update_wirechain(geom, key, poly_list, wirechain, datafield)

        for key, value in wirechain.items():
            geom.boolean_union(value)
            pygmsh.generate_mesh(geom, geo_filename=str(gds) + '_wirechain.geo')


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
        raise ValueError('Please specify a valid cell name')

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

    datafield = DataField('Hypres', config_file)

    cell = gdsii.extract(cellname)
    process.detect_components(cell, datafield)
    process.create_wirechains(cell, datafield)

    gmsh_wirechain(datafield)

    # TODO: unittest for data correctly connect to Polygon.
    # for poly in datafield.polygons:
    #     if poly.data:
    #         print(poly.data.name)

    # if model is True:
    #     geom = pygmsh.opencascade.Geometry()
    #
    #     geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.05;')
    #     geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.05;')
    #
    #     wc = modeling.wirechain(geom, cellname, config.auron_cell, configdata)
    #
    #     tc = modeling.terminals(wc, geom, config, configdata)

    datafield.parse_gdspy(gdsyuna.Cell('View Cell Test'))

    gdsyuna.LayoutViewer()
    gdsyuna.write_gds('auron.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.\n')

    return datafield
