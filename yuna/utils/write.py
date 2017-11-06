from __future__ import print_function
from termcolor import colored
from utils import tools


import gdspy
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri


def add_jj_cell(cell, config):
    """
        Add the JJ polygons to the main cell using a
        subcell. This is to label the JJ value with
        it's required values. The name of the JJ cell
        has to be different than the original, hence
        the 'yuna_' addition string.
    """

    for num, jj in enumerate(config['Layers']['JJ']['result']):
        jjname = 'yuna_' + config['Layers']['JJ']['name'][num]
        label = gdspy.Label(jjname, (0, 0), 'sw')

        cell_jj = gdspy.Cell(jjname)
        cell_jj.add(gdspy.Polygon(jj, 6))
        cell_jj.add(label)

        cell.add(cell_jj)


def add_polygons_to_cell(cell, item):
    """ Loop through the polygon list of
    the layer, subatom or module and add
    it to the gdspy library for processing."""

    for poly in item['result']:
        cell.add(gdspy.Polygon(poly, item['gds']))


def layers_cell(cell, Layers):
    for key, layer in Layers.items():
        if json.loads(layer['view']):
            layer['id'] = key
            add_polygons_to_cell(cell, layer)

    return cell


def modules_to_cell(cell, subatom):
    for module in subatom['Module']:
        for key, value in module.items():
            if key == 'via_connect':
                if json.loads(value['view']):
                    add_polygons_to_cell(cell, module)
            elif key == 'via_remove':
                if json.loads(value['view']):
                    add_polygons_to_cell(cell, module)
            elif key == 'jj_base':
                if json.loads(value['view']):
                    add_polygons_to_cell(cell, module)
            elif key == 'jj_diff':
                if json.loads(value['view']):
                    add_polygons_to_cell(cell, module)


def atom_cell(cell, Atom):
    for key, atom in Atom.items():
        print ('      ' + '-> ', end='')
        print('Atom: ' + str(atom['id']))

        if key == 'vias':
            for subatom in atom['Subatom']:
                if json.loads(subatom['view']):
                    print(subatom['module'])
                    add_polygons_to_cell(cell, subatom)
                # modules_to_cell(cell, subatom)
        elif key == 'jj':
            for subatom in atom['Subatom']:
                if json.loads(subatom['view']):
                    print(subatom['module'])
#                     add_polygons_to_cell(cell, subatom)
                modules_to_cell(cell, subatom)

    return cell


class Write:
    def __init__(self, view):
        self.view = view
        self.solution = None
        self.holes = None

    def write_gds(self, basedir, Layers, Atom, ldf):
        """
            Write the GDS file that contains the difference
            of the moat layer with the wiring layer and the
            union of the moat/wire layers.

            Notes
            -----
                * These three or more polygons combined will
                  represent the full union structure of the
                  wire layer, but with the area over the moat
                  known. The polygon area over the moat will
                  have a GDS number of 70.

                * Poly read into gdspy.Polygon must be a 1D list:
                  [[x,y], [x1,y1], [x2,y2]]

            Layer numbers
            -------------

                80 : Wire layer
                81 : Via
                72 : Ground polygons
                71 : JJ polygons
                70 : Holes
        """

        yunalayout = None

        tools.green_print('Cell: STEM - Hypres')
        yunacell = gdspy.Cell('STEM')
        yunacell = layers_cell(yunacell, Layers)
        yunacell = atom_cell(yunacell, Atom)

#         if ldf == 'adp':
#             tools.green_print('Cell: ADP - Japan')
#             yunacell = gdspy.Cell('ADP')
#             yunacell = adp_process(basedir, Layers, Atom)
#         elif ldf == 'stem64':
#             tools.green_print('Cell: STEM - Hypres')
#             yunacell = gdspy.Cell('STEM')
#             yunacell = layers_cell(yunacell, Layers)
#             yunacell = atom_cell(yunacell, Atom)
#         else:
#             print ('write.py -> Please specify a LDF file.')

        if self.view:
            gdspy.LayoutViewer()

        self.solution = yunacell.get_polygons(True)





