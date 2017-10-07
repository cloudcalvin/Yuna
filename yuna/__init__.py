from __future__ import print_function
from termcolor import colored

import os
import yuna.utils.read
import yuna.utils.write
import yuna.process
import json


def machina(gds, config, ldf):
    viewgds = True

    layers = yuna.utils.read.ldf(ldf)
    write = yuna.utils.write.Write(viewgds)

    return generate_gds(write, gds, layers, config, ldf)


def generate_gds(write, gds_file, layers, config_file, ldf):
    """
        Read in the layers from the GDS file,
        do clipping and send polygons to
        GMSH to generate the Mesh.
    """

    if (ldf == 'adp') or (ldf == 'stp'):
        print ('[' + colored('*', 'green') + '] ', end='')
        config_data = yuna.utils.read.config(config_file)

        # Process object
        process = yuna.process.Process(gds_file, config_data)
        config = process.config_layers()

        # Write object
        write = yuna.utils.write.Write(True)
        write.write_gds(config)

        return write.solution
    elif ldf == 'stem64':
        print ('[' + colored('*', 'green') + '] ', end='')
        print ('Using stem64 ldf file:')
        config_data = yuna.utils.read.config(config_file)

    else:
        raise Exception('Please specify the fabrication process')










