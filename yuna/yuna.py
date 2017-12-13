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

    process = arguments['<process>']
    testname = arguments['<testname>']
    ldf = arguments['<ldf>']

    if arguments['--cell'] == 'list':
        cellref = 'list'
    elif arguments['--cell']:
        cellref = arguments['--cell']
    else:
        cellref = ""

    machina(process, testname, ldf, cellref, '', False)

    tools.red_print('Auron. Done.')


def machina(process, testname, ldf, cellref, cwd, union):
    """  """

    tools.cyan_print('Running Yuna...')

    if cwd == '':
        cwd = os.getcwd()

    basedir = cwd + '/tests/' + process
    examdir = basedir + '/' + testname

    gds_file = examdir + '/' + testname + '.gds'
    config_file = examdir + '/' + testname + '.json'

    wires = None

    layers = read.ldf(ldf)

    if cellref == 'list':
        tools.list_layout_cells(gds_file)
    else:
        fincell, Params, Layers = generate_gds(examdir, gds_file, layers, config_file, ldf, cellref, union)

    tools.cyan_print('Yuna. Done.')

    return fincell, Params, Layers


def generate_gds(examdir, gds_file, layers, config_file, ldf, cellref, union):
    """ Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh. """

    config_data = read.config(config_file)
    
    tools.magenta_print('Process Layers')
    auron_cell = gdspy.Cell('auron_cell')

    config = process.Config(config_data)
    config.set_gds(gds_file)

    if cellref:
        config.read_usercell_reference(cellref, auron_cell)
    else:
        config.read_topcell_reference()

    # config.parse_gdspy_elements()

    # proc = process.Process(examdir, config)
    # proc.circuit_layout(union)

    # jjs = config.jjs
    # vias = config.vias
    # wireset = proc.wiresets
    # terms = config.Terms

    # tools.magenta_print('Write Layers')
    # cWrite = write.Write(True)
    # gdssetup = cWrite.write_gds(examdir, ldf, jjs, vias, wireset)
    
    gdspy.LayoutViewer()
    gdspy.write_gds('bbn_basic_cell.gds', unit=1.0e-6, precision=1.0e-6)

    return auron_cell, config_data['Params'], config_data['Layers']


if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
