import gmsh
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
            cell.add(gdspy.Polygon(poly, 81))
        for poly in config['Layers']['COU']['result']:
            cell.add(gdspy.Polygon(poly, 91))
        for poly in config['Layers']['CTL']['result']:
            cell.add(gdspy.Polygon(poly, 92))
        for poly in config['Layers']['JJ']['result']:
            cell.add(gdspy.Polygon(poly, 93))
        for poly in config['Layers']['COU']['jj']:
            cell.add(gdspy.Polygon(poly, 94))
        for poly in config['Layers']['TERM']['result']:
            cell.add(gdspy.Polygon(poly, 95))

        if (self.view):
            gdspy.LayoutViewer()

        self.solution = cell.get_polygons(True)

    def plot_mesh(self, cMesh):
        x_center = cMesh.matrix_centers[:, 0]
        y_center = cMesh.matrix_centers[:, 1]

        x = cMesh.matrix_node[:, 0]
        y = cMesh.matrix_node[:, 1]

        triang = tri.Triangulation(x, y, cMesh.matrix_triangle)

        zfaces = None
        zfaces = np.zeros(len(cMesh.matrix_triangle))

        plt.figure()
        plt.gca().set_aspect('equal')
        plt.triplot(triang, 'ko-')
        plt.tripcolor(x, y, cMesh.matrix_triangle,
                      facecolors=zfaces,
                      edgecolor='#cc33ff')
        plt.plot(x_center, y_center, 'ro')

        for i in range(len(cMesh.matrix_edge)):
            line_array = np.array([])
            id_1 = cMesh.matrix_edge[i][0]-1
            id_2 = cMesh.matrix_edge[i][1]-1

            node_1 = cMesh.matrix_centers[id_1]
            node_2 = cMesh.matrix_centers[id_2]

            if (len(line_array) == 0):
                line_array = np.append(line_array, [node_1])
                line_array = np.vstack([line_array, [node_2]])

            line_x = line_array[:, 0]
            line_y = line_array[:, 1]

            plt.plot(line_x, line_y, 'g-')

        plt.title('Triangular grid')
        plt.show()
