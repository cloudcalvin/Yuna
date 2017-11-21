from __future__ import print_function
from termcolor import colored
from yuna.utils import tools


import gdspy
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri


class Write:
    """  """

    def __init__(self, view):
        self.view = view
        self.holes = None

    def write_gds(self, basedir, ldf, jjs, vias, wireset_list):
        """ Write polygons to a new GDS cell using
        gdspy. The polygons written are read from
        the updated JSON Config file. """

        tools.green_print('Cell: STEM - Hypres')
        cell = gdspy.Cell('STEM')

#         for via in vias:
#             via.plot_via(cell)
#         for jj in jjs:
#             jj.plot_jj(cell)
        for wireset in wireset_list:
            for wire in wireset.wires:
                wire.plot_wire(cell, wireset.gds)

        if self.view:
            gdspy.LayoutViewer()

        return cell.get_polygons(True)
