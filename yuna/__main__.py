# """
# 
# Usage:
#     yuna <process> <testname> <ldf> [--cell=<cellname>] [(<atom_num> <subatom_num>)]
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
# from docopt import docopt
# from yuna.utils import tools
# 
# 
# def main():
#     """  """
# 
#     arguments = docopt(__doc__, version='Yuna 0.1.0')
#     tools.red_print('Summoning Yuna...')
#     tools.parameter_print(arguments)
# 
#     process = arguments['<process>']
#     testname = arguments['<testname>']
#     ldf = arguments['<ldf>']
# 
#     if arguments['--cell'] == 'list':
#         cellref = 'list'
#     elif arguments['--cell']:
#         cellref = arguments['--cell']
#     else:
#         cellref = ""
# 
#     machina(process, testname, ldf, cellref, '')
# 
#     tools.red_print('Auron. Done.')
# 
# 
# if __name__ == '__main__':
#     main()
