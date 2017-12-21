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
import yuna.read as read

from yuna.utils import write
from yuna.utils import tools

from pprint import pprint


def main():
    """  """

    arguments = docopt(__doc__, version='Yuna 0.1.0')
    tools.red_print('Summoning Yuna...')
    tools.parameter_print(arguments)

    if arguments['--cell'] == 'list':
        cellref = 'list'
    elif arguments['--cell']:
        machina(arguments, '', False)
    else:
        cellref = ""

    tools.red_print('Auron. Done.')


def machina(args, cwd):
    """  """

    tools.cyan_print('Running Yuna...')
    
    process = args['<process>']
    testname = args['<testname>']
    ldf = args['<ldf>']

    if cwd == '':
        cwd = os.getcwd()

    basedir = cwd + '/tests/' + process
    examdir = basedir + '/' + testname
    gds_file = examdir + '/' + testname + '.gds'
    config_file = examdir + '/' + 'config.json'

    tools.cyan_print('Yuna. Done.')

    return generate_gds(examdir, gds_file, config_file, args['--cell'], args['--union'])


def generate_gds(examdir, gds_file, config_file, cellref, union):
    """ Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh. """
    
    tools.magenta_print('Process Layers')
    auron_cell = gdspy.Cell('Auron Cell')

    data = read.config(config_file)
    config = process.Config(data)
    config.set_gds(gds_file)

    if cellref:
        config.read_usercell_reference(cellref, auron_cell)
    else:
        config.read_topcell_reference()

    gdspy.LayoutViewer()
    gdspy.write_gds('bbn_basic_cell.gds', unit=1.0e-6, precision=1.0e-6)

    return auron_cell, data['Params'], data['Layers']


if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
