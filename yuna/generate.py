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


from __future__ import print_function
from __future__ import absolute_import

from docopt import docopt
from termcolor import colored

import os
import json
import gdspy

import yuna.process as process

from yuna.utils import write
from yuna.utils import tools

from pprint import pprint


# def main():
#     """  """
# 
#     arguments = docopt(__doc__, version='Yuna 0.1.0')
#     tools.red_print('Summoning Yuna...')
#     tools.parameter_print(arguments)
# 
#     if arguments['--cell'] == 'list':
#         cellref = 'list'
#     elif arguments['--cell']:
#         machina(arguments, '', False)
#     else:
#         cellref = ""
# 
#     tools.red_print('Auron. Done.')

    
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

    auron_cell = gdspy.Cell('Auron Cell')
    if args['--cell']:
        config.read_usercell_reference(args['--cell'], auron_cell)
    else:
        config.read_topcell_reference()

    gdspy.LayoutViewer()
    gdspy.write_gds('bbn_basic_cell.gds', unit=1.0e-6, precision=1.0e-6)

    tools.cyan_print('Yuna. Done.')
    
    return auron_cell, data['Params'], data['Layers']


if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
