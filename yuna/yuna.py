"""

Usage:
    yuna <process> <testname> <ldf> [--cell=<cellname>] [(<atom_num> <subatom_num>)]
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

import yuna.process as proc
import yuna.read as read

from yuna.utils import write
from yuna.utils import tools


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

    machina(process, testname, ldf, cellref, '')

    tools.red_print('Auron. Done.')


def machina(process, testname, ldf, cellref, cwd):
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
        wires = generate_gds(examdir, gds_file, layers, config_file, ldf, cellref)

    tools.cyan_print('Yuna. Done.')

    return wires


def generate_gds(examdir, gds_file, layers, config_file, ldf, cellref):
    """ Read in the layers from the GDS file,
    do clipping and send polygons to
    GMSH to generate the Mesh. """

    config_data = read.config(config_file)

    tools.magenta_print('Process Layers')
    cProcess = proc.Process(examdir, gds_file, config_data)
    cProcess.config_layers(cellref)

    jjs = cProcess.jjs
    vias = cProcess.vias
    wires = cProcess.wires

    tools.magenta_print('Write Layers')
    cWrite = write.Write(True)
    gdssetup = cWrite.write_gds(examdir, ldf, jjs, vias, wires)

    return wires


if __name__ == '__main__':
    main()
