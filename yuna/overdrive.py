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


def grand_summon(basedir, cell, cwd):
    """ Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh. """

    tools.cyan_print('Running Yuna...')

    if not cell:
        raise ValueError('not a valid cell name')
    
    gds_file, config_file = '', ''
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.gds'):
                gds_file = basedir + '/' + file
            elif file.endswith('.json'):
                if file == 'config.json':
                    config_file = basedir + '/' + file

    tools.green_print(config_file)
    configdata = read_config(config_file)

    config = process.Config(configdata)
    config.init_gds_layout(gds_file)

    config.create_yuna_flatten(cell)
    config.create_auron_polygons()
    config.add_auron_labels()

    gdsyuna.LayoutViewer()
    gdsyuna.write_gds('bbn_basic_cell.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.')

    return config.auron_cell, configdata
    
    
    
    
    
    
    
    
    
    
    
    
    
