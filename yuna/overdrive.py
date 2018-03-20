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
from yuna import structure


def geom_wirechain(datafield):
    """

    """

    geom = pygmsh.opencascade.Geometry()

    geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
    geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

    layers = datafield.get_polygons()

    wirechain = list()
    for key, value in layers.items():
        if key[0] == 6:
            for i, points in enumerate(layers[key]):
                for pp in points:
                    polyname = 'name' + '_' + str(i)
                    poly = geom.add_polygon(pp, lcar=0.1, make_surface=True)
                    geom.add_physical_surface(poly.surface, label=str(key)+str(i))
                    wirechain.append(poly.surface)

    geom.boolean_union(wirechain)

    pygmsh.generate_mesh(geom, geo_filename='wirechain.geo')

    # meshio.write('3d_model.vtk', *layer_mesh)


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

    pdd = tools.read_config(config_file)

    datafield = structure.DataField('Hypres')

    cell = gdsii.extract(cellname)
    process.detect_components(cell, pdd, datafield)
    process.create_wirechains(pdd, cell, datafield)

    geom_wirechain(datafield)

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

    return my_cell, pdd
