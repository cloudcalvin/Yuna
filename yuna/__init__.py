import os
import yuna.utils.read
import yuna.utils.write
import yuna.process


def machina(gds, config, ldf):
    # os.chdir('..')
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

    # cwd = os.getcwd()
    # gds_file = cwd + '/tests/gds/' + file_name + '.gds'
    # config_file = cwd + '/yuna/' + 'config.json'

    if (ldf == 'adp') or (ldf == 'stp'):
        config_data = yuna.utils.read.config(config_file)

        # Process object
        process = yuna.process.Process(gds_file, config_data)
        config = process.config_layers()

        # Write object
        write = yuna.utils.write.Write(True)
        write.write_gds(config)

        return write.solution
    else:
        raise Exception('Please specify the fabrication process')
