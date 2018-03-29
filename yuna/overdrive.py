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
import pygmsh
import gdsyuna

from docopt import docopt

from yuna import process
from yuna import tools
from yuna import modeling
from yuna import deck

from .datafield import DataField


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

    if model is True:
        geom = pygmsh.opencascade.Geometry()

        geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.1;')
        geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.1;')

        geom.add_raw_code('Mesh.Algorithm = 100;')
        geom.add_raw_code('Coherence Mesh;')

        wc = modeling.wirechain(geom, datafield)

    #     tc = modeling.terminals(wc, geom, config, configdata)

        meshdata = pygmsh.generate_mesh(geom, verbose=False, geo_filename='3D.geo')

        # meshio.write('3D.vtu', *meshdata)

    gdsyuna.LayoutViewer()
    gdsyuna.write_gds('auron.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.\n')

    return datafield
