from __future__ import print_function
from termcolor import colored
from utils import tools


import gdspy
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri


# def add_vias_to_cell(cell, vias):
#     """ Loop over the vias object 
#     list and plot the 'base' polygons. """
# 
#     for via in vias:
#         via.plot_via(cell)
# 
# 
# def add_jj_to_cell(cell, jjs):
#     """ Loop through the polygon list of
#     the layer, subatom or module and add
#     it to the gdspy library for processing."""
# 
#     for jj in jjs:
#         jj.plot_jj(cell)
# 
# 
# def add_wires_to_cell(cell, wires):
#     """  """
#     for wire in wires:
#         wire.plot_wire(cell)


class Write:
    def __init__(self, view):
        self.view = view
        self.solution = None
        self.holes = None

    def write_gds(self, basedir, Layers, Atom, ldf, jjs, vias, wires):
        """ Write polygons to a new GDS cell using
        gdspy. The polygons written are read from
        the updated JSON Config file. """

        tools.green_print('Cell: STEM - Hypres')
        cell = gdspy.Cell('STEM')

        for via in vias:
            via.plot_via(cell)
        for jj in jjs:
            jj.plot_jj(cell)
        for wire in wires:
            wire.plot_wire(cell)

#         add_jj_to_cell(cell, jjs)
#         add_vias_to_cell(cell, vias)
#         add_wires_to_cell(cell, wires)

        if self.view:
            gdspy.LayoutViewer()

        self.solution = cell.get_polygons(True)







