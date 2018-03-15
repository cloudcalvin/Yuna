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


def process_data(fabdata):
    pdd = process.ProcessData('Hypres', fabdata)

    pdd.add_parameters(fabdata['Params'])
    pdd.add_atoms(fabdata['Atoms'])
    pdd.add_wires()
    pdd.add_vias()
    pdd.add_junctions()

    for key, value in pdd.junctions.items():
        print(key)

    return pdd


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

    tools.green_print(config_file)
    jsondata = tools.read_config(config_file)

    gdsii = gdsyuna.GdsLibrary()
    gdsii.read_gds(gds_file, unit=1.0e-12)

    pdd = process_data(jsondata)

    cell_wirechain = gdsyuna.Cell('Wirechain Cell')
    cell_layout = process.create_cell_layout(gdsii, cellname, pdd)

    process.add_terminals(pdd, cell_layout, cell_wirechain)
    process.create_wirechains(pdd, cell_layout, cell_wirechain)
    process.add_component_labels(pdd, cell_layout, cell_wirechain)

    # if model is True:
    #     geom = pygmsh.opencascade.Geometry()
    #
    #     geom.add_raw_code('Mesh.CharacteristicLengthMin = 0.05;')
    #     geom.add_raw_code('Mesh.CharacteristicLengthMax = 0.05;')
    #
    #     wc = modeling.wirechain(geom, cellname, config.auron_cell, configdata)
    #
    #     tc = modeling.terminals(wc, geom, config, configdata)

    gdsyuna.LayoutViewer()
    gdsyuna.write_gds('auron.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.\n')

    return cell_wirechain, pdd
