from __future__ import print_function # lace this in setup.
from termcolor import colored

import gdspy
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


class Write:
    def __init__(self, view):
        self.view = view
        self.solution = None
        self.holes = None

    def write_gds(self, config):
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

        print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
        print('Cell: SOLUTION')
        cell = gdspy.Cell('SOLUTION')
        
        # add_jj_cell(cell, config)
        
        # for poly in config['Layers']['RC']['jj']:
        #     cell.add(gdspy.Polygon(poly, 20))
        print ('      ' + '-> ', end='')
        print('RES JJ')
        for poly in config['Layers']['RES']['jj']:
            cell.add(gdspy.Polygon(poly, 21))
        
        print ('      ' + '-> ', end='')
        print('CC')
        for poly in config['Layers']['CC']['result']:
            cell.add(gdspy.Polygon(poly, 11))
            
        print ('      ' + '-> ', end='')
        print('COU')
        for poly in config['Layers']['COU']['result']:
            cell.add(gdspy.Polygon(poly, 8))
            
        print ('      ' + '-> ', end='')
        print('CTL')
        for poly in config['Layers']['CTL']['result']:
            cell.add(gdspy.Polygon(poly, 12))
            
        print ('      ' + '-> ', end='')
        print('COU JJ')
        for poly in config['Layers']['COU']['jj']:
            cell.add(gdspy.Polygon(poly, 108))
            
        print ('      ' + '-> ', end='')
        print('TERM')
        for poly in config['Layers']['TERM']['result']:
            cell.add(gdspy.Polygon(poly, 15))

        if self.view:
            gdspy.LayoutViewer()

        self.solution = cell.get_polygons(True)












