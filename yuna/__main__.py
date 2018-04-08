# """
# 
# Usage:
#     yuna <process> <testname> <ldf> [--cell=<cellname>] [--union] [--model]
#     yuna (-h | --help)
#     yuna (-V | --version)
# 
# Options:
#     -h --help     Show this screen.
#     -p --pretty   Prettify the output.
#     -V --version  Show version.
#     --quiet       print less text
#     --verbose     print more text
# 
# """
# 
# 
# import os
# import json
# import gdspy
# 
# from docopt import docopt
# from yuna import process
# from yuna import utils
# 
# 
# def read_config(config_file):
#     """ Reads the config file that is written in
#     JSON. This file contains the logic of how
#     the different layers will interact. """
# 
#     data = None
#     with open(config_file) as data_file:
#         data = json.load(data_file)
#     return data
# 
# 
# def main(args, cwd):
#     """ Read in the layers from the GDS file,
#     do clipping and send polygons to
#     GMSH to generate the Mesh. """
# 
#     utils.cyan_print('Running Yuna...')
# 
#     gds_file, config_file = '', ''
#     for root, dirs, files in os.walk(os.getcwd()):
#         for file in files:
#             if file.endswith('.gds'):
#                 gds_file = os.getcwd() + '/' + file
#             elif file.endswith('.json'):
#                 config_file = os.getcwd() + '/' + file
# 
#     configdata = read_config(config_file)
# 
#     config = process.Config(configdata)
#     config.init_gds_layout(gds_file)
# 
#     if args['--cell']:
#         config.create_yuna_flatten(args['--cell'])
#         config.create_auron_polygons()
#         config.add_auron_labels()
#     else:
#         print('Please specify a Cell')
# 
#     gdspy.LayoutViewer()
#     gdspy.write_gds('bbn_basic_cell.gds', unit=1.0e-6, precision=1.0e-6)
# 
#     utils.cyan_print('Yuna. Done.')
# 
#     return config.auron_cell, configdata
# 
# 
# if __name__ == '__main__':
#     main()
# 
# 
# 
# 
# 
# 
# 
