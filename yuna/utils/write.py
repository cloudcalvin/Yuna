import gdspy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from graph_tool.all import *


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

        cell = gdspy.Cell('SOLUTION')

        for poly in config['Layers']['CC']['result']:
            cell.add(gdspy.Polygon(poly, 11))
        for poly in config['Layers']['COU']['result']:
            cell.add(gdspy.Polygon(poly, 8))
        for poly in config['Layers']['CTL']['result']:
            cell.add(gdspy.Polygon(poly, 12))
        for poly in config['Layers']['JJ']['result']:
            cell.add(gdspy.Polygon(poly, 6))
        for poly in config['Layers']['COU']['jj']:
            cell.add(gdspy.Polygon(poly, 108))
        for poly in config['Layers']['TERM']['result']:
            cell.add(gdspy.Polygon(poly, 15))

        if self.view:
            gdspy.LayoutViewer()

        self.solution = cell.get_polygons(True)
