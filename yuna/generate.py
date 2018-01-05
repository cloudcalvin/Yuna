"""

Usage:
    yuna <process> <testname> <ldf> [--cell=<cellname>] [--union] [--model]
    yuna (-h | --help)
    yuna (-V | --version)

Options:
    -h --help     Show this screen.
    -p --pretty   Prettify the output.
    -V --version  Show version.
    --quiet       print less text
    --verbose     print more text

"""


import os
import json
import gdsyuna

from docopt import docopt
from yuna import process
from yuna import tools


def read_config(config_file):
    """ Reads the config file that is written in
    JSON. This file contains the logic of how
    the different layers will interact. """

    data = None
    with open(config_file) as data_file:
        data = json.load(data_file)
    return data


def machina(args, cwd):
    """ Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh. """

    tools.cyan_print('Running Yuna...')
    
    if cwd == '':
        cwd = os.getcwd()

    examdir = cwd + '/tests/' + args['<process>'] + '/' + args['<testname>']
    gds_file = examdir + '/' + args['<testname>'] + '.gds'
    config_file = examdir + '/' + 'config.json'

    data = read_config(config_file)
    config = process.Config(data)
    config.set_gds(gds_file)

    auron_cell = gdsyuna.Cell('Auron Cell')
    if args['--cell']:
        config.read_usercell_reference(args['--cell'], auron_cell)
    else:
        config.read_topcell_reference()

    gdsyuna.LayoutViewer()
    gdsyuna.write_gds('bbn_basic_cell.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.')
    
    return auron_cell, data['Params'], data['Layers']


    
    
    
    
    
    
