from __future__ import print_function
from termcolor import colored
from yuna.utils import tools


import gdsyuna
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri


class Write:
    """  """

    def __init__(self, view):
        self.view = view
        self.holes = None

    def write_gds(self, basedir, ldf, jjs, vias, wiresets):
        """ Write polygons to a new GDS cell using
        gdsyuna. The polygons written are read from
        the updated JSON Config file. """

        tools.green_print('Cell: STEM - Hypres')
        cell = gdsyuna.Cell('STEM')

        # for via in vias:
        #     via.plot_via(cell)
        # for jj in jjs:
        #     jj.plot_jj(cell)
        for key, wireset in wiresets.items():
            for wire in wireset.wires:
                wire.plot_wire(cell, wireset.gds)

        if self.view:
            gdsyuna.LayoutViewer()

        return cell.get_polygons(True)
