import os
import yuna.utils.read
import yuna.utils.write
import yuna.process


def machina(gds, ldf):
    # os.chdir('..')
    viewgds = True

    layers = yuna.utils.read.ldf(ldf)
    write = yuna.utils.write.Write(viewgds)

    generate_gds(write, gds, layers, ldf)


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
        config_data = yuna.utils.read.config(config_file)

        # Process object
        process = yuna.process.Process(gds_file, config_data)
        config = process.config_layers()

        # Write object
        write = yuna.utils.write.Write(True)
        write.write_gds(config)
    else:
        raise Exception('Please specify the fabrication process')
