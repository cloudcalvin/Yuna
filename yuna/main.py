"""HTML Cleaner.

Usage:
    yuna [--quiet | --verbose] <gds> <ldf>
    yuna [-p | --pretty] <element> <replacement> <filename>
    yuna (-h | --help)
    yuna (-V | --version)

Options:
    -h --help     Show this screen.
    -p --pretty   Prettify the output.
    -V --version  Show version.
    --quiet       print less text
    --verbose     print more text

"""


from docopt import docopt
import auron.read

import utils.tools
import os
import auron.process
import auron.io


"""
    Hacker: 1h3d*n
    For: Volundr
    Docs: Algorithm 1
    Date: 31 April 2017

    Description: Morph the moat layer and the wire layers.

    1) Get a list of all the polygons inside the GDS file.
    2) Send this list to the Clip library with the wiring
       layer number and the moat layer number as parameters.
    3) Get the union of all the wiring layer polygons that
       are connected. Update this to check for vias.
    4) Get the intersection of the moat layer with the
       wiring layer and save this in a new polygon.
    5) Get the difference of the moat layer with the
       wiring layer and save this in a new polygon.
    6) Join the intersected and difference polygons
       to form a list of atleast 3 polygons.
    7) We now know which part of the wiring layer
       goes over the moat is most probably mutually
       connected to wiring layer 2.
    8) Send this polygon structure to GMSH.
"""


def main():
    """
        Example of minimum compile options:
            * adp - is the fabrication process used.
            * test - is the gds file used.
    """

    print 'Number of Processors: ' + str(utils.tools.number_of_processors())

    arguments = docopt(__doc__, version='Yuna 0.0.1')
    ldf = arguments['<ldf>']
    gds = arguments['<gds>']

    os.chdir('..')
    viewgds = True

    layers = auron.read.ldf(ldf)
    write = io.write.Write(viewgds)

    generate_gds(write, gds, layers, ldf)

    print '\nEnd of program\n'


def generate_gds(write, file_name, layers, process):
    """
        Read in the layers from the GDS file,
        do clipping and send polygons to
        GMSH to generate the Mesh.
    """

    cwd = os.getcwd()
    gds_file = cwd + '/tests/gds/' + file_name + '.gds'
    config_file = cwd + '/yuna/' + 'config.json'

    if (process == 'adp') or (process == 'stp'):
        config_data = read_config(config_file)
        process = auron.process.Process(gds_file, config_data)
        config = process.config_layers()
        write.write_gds(config)
    else:
        raise Exception('Please specify the fabrication process')


if __name__ == '__main__':
    main()
