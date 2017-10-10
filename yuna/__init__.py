from __future__ import print_function
from termcolor import colored

import os
import json
import gdspy

import yuna.utils.read as read
import yuna.utils.write as write
import yuna.process as process
import yuna.utils.tools as tools


def machina(basedir, gds, config_file, ldf, cellref):
    print ('\n' + '[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Running Yuna...')

    gdssetup = None

    layers = read.ldf(ldf)

    if cellref == 'list':
        tools.list_layout_cells(gds)
    else:
        gdssetup = generate_gds(basedir, gds, layers, config_file, ldf, cellref)

    print ('\n[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Yuna. Done.')

    return gdssetup


def generate_gds(basedir, gds_file, layers, config_file, ldf, cellref):
    """
        Read in the layers from the GDS file,
        do clipping and send polygons to
        GMSH to generate the Mesh.
    """
    
    config_data = read.config(config_file)

    tools.magenta_print('Process Layers')
    cProcess = process.Process(basedir, gds_file, config_data)
    config = cProcess.config_layers(cellref)

    tools.magenta_print('Write Layers')
    cWrite = write.Write(True)
    cWrite.write_gds(basedir, config, ldf)






























