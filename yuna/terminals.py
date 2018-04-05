import gdsyuna
import pygmsh
import meshio
import numpy as np
import pyclipper

from yuna import tools
from collections import namedtuple


class Terminal(object):
    
    def __init__(self, points):
        self.points = points
        self.centerline = None 
        self.metals = list()
        
    def set_centerline(self):
        pass
        
    def metal_connection(self, cell, datafield, name):
        for gds, metal in datafield.wires.items():
            m1 = name.split(' ')[1]
            m2 = name.split(' ')[2]

            # TODO: Solve this fucking issue with the ground M0.
            if metal.name in [m1, m2]: 
                self.metals.append(gds)
                
        print(self.metals)
    
    def metal_edges(self):
        pass 
        
    def parallel_edge(geom, cell, datafield):
        pass
    
    
def metals_edge(geom, datafield):
    """
    Extract the terminals on the edges of a layer.

    Notes
    -----
    The y-direction sideconnects have a key entry of (99, 0).
    The x-direction sideconnects have a key entry of (99, 1).
    """

    for gds, polygons in datafield.polygons.items():
        print(gds)

        datatype = 0
        if datatype in polygons:
            for poly in polygons[datatype]:
                points = np.vstack([poly.points, poly.points[0]])

                for p1, p2 in zip(points[:-1], points[1:]):
                    bb = np.array([p1, p2, p2, p1])

                    sc_width = 10e4

                    for i in [0, 1]:
                        # if abs(p1[i] - p2[i]) < 1e-6:
                        bb[0][i] += sc_width
                        bb[1][i] += sc_width
                        bb[2][i] -= sc_width
                        bb[3][i] -= sc_width

                    polygon = gdsyuna.Polygon(bb, layer=99, datatype=0, verbose=False)
                    side_cell.add(polygon)

                    side = Sideconnect([p1.tolist(), p2.tolist()], bb, layer=99, datatype=0, verbose=False)
                    sideconnects.append(side)

    # # TODO: Test for multiple layers in the wirechain.
    # for gds, layer in jsondata['Layers'].items():
    #     if layer['type'] == 'wire' and (int(gds), 0) in config.yuna_polygons:
    #         points = config.yuna_polygons[(int(gds), 0)]
    #         points = np.vstack([points[0], points[0][0]])
    #
    #         for p1, p2 in zip(points[:-1], points[1:]):
    #
    #             bb = np.array([p1, p2, p2, p1])
    #
    #             sc_width = 10e4
    #
    #             for i in [0, 1]:
    #                 if abs(p1[i] - p2[i]) < 1e-9:
    #                     bb[0][i] += sc_width
    #                     bb[1][i] += sc_width
    #                     bb[2][i] -= sc_width
    #                     bb[3][i] -= sc_width
    #
    #             polygon = gdsyuna.Polygon(bb, layer=99, datatype=0, verbose=False)
    #             side_cell.add(polygon)
    #
    #             side = Sideconnect([p1, p2], bb, layer=99, datatype=0, verbose=False)
    #             sideconnects.append(side)

    terminal_line(geom, sideconnects, datafield)


def line_length(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def terminal_line(geom, sideconnects, datafield):
    """
    Notes
    -----
    The y-direction sideconnects have a key entry of (99, 0).
    The x-direction sideconnects have a key entry of (99, 1).
    """

    print('--- running terminal lines ---------')

    terminal_sides = list()

    for side in sideconnects:
        paths = None
        for polygon in datafield.polygons[63][0]:

            pc = pyclipper.Pyclipper()

            pc.AddPaths([side.edge], pyclipper.PT_SUBJECT, False)
            pc.AddPaths([polygon.points], pyclipper.PT_CLIP, True)

            solution = pc.Execute2(pyclipper.CT_INTERSECTION,
                                   pyclipper.PFT_NONZERO,
                                   pyclipper.PFT_NONZERO)

            paths = pyclipper.PolyTreeToPaths(solution)

            pp = paths[0]

            if pp:
                print(pp)
                p_len = line_length(pp[0], pp[1])
                print(p_len)
                print('')
                terminal_sides.append(side.edge)

            # if paths:
            #     terminal_sides.append(side.edge)

            # for ipoly in tools.angusj([side.edge], [polygon.points], 'intersection', closed=False):
            # for ipoly in tools.angusj([polygon.points], [side.edge], 'intersection'):
                # print(ipoly)
                # terminal_sides.append(ipoly)
                # if poly.area() > (0.7 * side.area()):
                    # terminal_sides.append(side)

    check_terminal_sides(terminal_sides)
    # geom_extrude_terminals(geom, terminal_sides, datafield)


# TODO: Future test maybe?
def check_terminal_sides(terminal_sides):
    term_side_cell = gdsyuna.Cell('Termrinal Sideconnect Cell')

    for path in terminal_sides:
        print(path)
        print('')
        poly = gdsyuna.Polygon(path, layer=99, datatype=0)
        term_side_cell.add(poly)

    # for side in sideconnects:
    #     poly = gdsyuna.Polygon(side.edge, layer=side.layer, datatype=side.datatype)
    #     term_side_cell.add(poly)
