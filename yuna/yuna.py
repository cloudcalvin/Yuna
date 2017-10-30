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
from termcolor import colored
from docopt import docopt

import os
import json
import gdspy
import process
import read

from utils import write
from utils import tools

# To run seperately:
# $ python yuna/yuna.py.
# Before distributing we have to comment __main__.


def print_parameters(arguments):
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print ('Parameters:')
    for key, value in arguments.items():
        print('      ' + str(key) + ' : ' + str(value))


def main():
    """
        Example of minimum compile options:
            * adp - is the fabrication process used.
            * test - is the gds file used.
    """

    arguments = docopt(__doc__, version='Yuna 0.1.0')
    tools.red_print('Summoning Yuna...')
    print_parameters(arguments)

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
    print ('\n' + '[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Running Yuna...')

    if cwd == '':
        cwd = os.getcwd()

    basedir = cwd + '/tests/' + process
    examdir = basedir + '/' + testname

    gds_file = examdir + '/' + testname + '.gds'
    config_file = examdir + '/' + testname + '.json'

    print (basedir)
    print (examdir)
    print (gds_file)
    print (config_file)

    gdssetup = None

    layers = read.ldf(ldf)

    if cellref == 'list':
        tools.list_layout_cells(gds)
    else:
        gdssetup = generate_gds(examdir, gds_file, layers, config_file, ldf, cellref)

    print ('\n[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Yuna. Done.')

    return gdssetup


def generate_gds(examdir, gds_file, layers, config_file, ldf, cellref):
    """
        Read in the layers from the GDS file,
        do clipping and send polygons to
        GMSH to generate the Mesh.
    """

    config_data = read.config(config_file)

    tools.magenta_print('Process Layers')
    cProcess = process.Process(examdir, gds_file, config_data)
    config = cProcess.config_layers(cellref)

    tools.magenta_print('Write Layers')
    cWrite = write.Write(True)
    cWrite.write_gds(examdir, config, ldf)


if __name__ == '__main__':
    main()






