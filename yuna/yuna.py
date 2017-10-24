from __future__ import print_function
from termcolor import colored

import os
import json
import gdspy

import utils.read as read
import utils.write as write
import process as process
import utils.tools as tools


def machina(process, testname, ldf, cellref):
    print ('\n' + '[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Running Yuna...')

    # os.chdir('..')

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
    machina('hypres', 'bbn_basic_cell', 'stem64', '')
