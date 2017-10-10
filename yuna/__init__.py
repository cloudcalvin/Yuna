from __future__ import print_function
from termcolor import colored

import os
import yuna.utils.read
import yuna.utils.write
import yuna.process
import json
import gdspy


def list_layout_cells(gds):
    """ List the Cells in the GDS layout. """

    gdsii = gdspy.GdsLibrary()
    gdsii.read_gds(gds, unit=1.0e-12)

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Cell List:')        
    for key, value in gdsii.cell_dict.items():
        print('      -> ' + key)


def machina(basedir, gds, config_file, ldf, cellref):
    print ('\n' + '[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Running Yuna...')

    viewgds = True
    gdssetup = None

    layers = yuna.utils.read.ldf(ldf)
    write = yuna.utils.write.Write(viewgds)

    if cellref == 'list':
        list_layout_cells(gds)
    else:
        gdssetup = generate_gds(basedir, write, gds, layers, config_file, ldf, cellref)

    print ('\n[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print ('Yuna. Done.')

    return gdssetup


def generate_gds(basedir, write, gds_file, layers, config_file, ldf, cellref):
    """
        Read in the layers from the GDS file,
        do clipping and send polygons to
        GMSH to generate the Mesh.
    """
    
    config_data = yuna.utils.read.config(config_file)

    print ('\n' + '[' + colored('*', 'magenta', attrs=['bold']) + '] ', end='')
    print ('--- Process Layers ----------')
    process = yuna.process.Process(basedir, gds_file, config_data)
    config = process.config_layers(cellref)

    print ('\n' + '[' + colored('*', 'magenta', attrs=['bold']) + '] ', end='')
    print ('--- Write Layers ----------')
    write = yuna.utils.write.Write(True)
    write.write_gds(basedir, config, ldf)

    # if (ldf == 'adp') or (ldf == 'stp'):
    #     config_data = yuna.utils.read.config(config_file)
    # 
    #     print ('\n' + '[' + colored('*', 'magenta', attrs=['bold']) + '] ', end='')
    #     print ('--- Process Layers ----------')
    #     process = yuna.process.Process(gds_file, config_data)
    #     config = process.config_layers(cellref)
    # 
    #     print ('\n' + '[' + colored('*', 'magenta', attrs=['bold']) + '] ', end='')
    #     print ('--- Write Layers ----------')
    #     write = yuna.utils.write.Write(True)
    #     write.write_gds(config, ldf)
    # 
    #     return write.solution
    # elif ldf == 'stem64':
    #     print ('\n' + '[' + colored('*', 'green') + '] ', end='')
    #     print ('Using stem64 ldf file:')
    #     config_data = yuna.utils.read.config(config_file)
    # else:
    #     raise Exception('Please specify the fabrication process')
































