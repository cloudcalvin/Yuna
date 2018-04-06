import gdsyuna
import pygmsh
import meshio
import numpy as np
import pyclipper

from yuna import tools
from collections import namedtuple


class Terminal(object):
    _ID = 0

    def __init__(self, points):
        self.id = 't{}'.format(Terminal._ID)
        Terminal._ID += 1

        self.points = points[0]
        self.edge = []
        self.slope = None
        self.metals = list()

    def square_loop(self, geom, datafield):
        polygon = datafield.polygons[self.metals[0]][0]

        print(polygon[0].data.name)

        s = polygon[0].data.z_start * 10e-6
        h = polygon[0].data.height * 10e-6

        pb = [[p[0]*10e-9, p[1]*10e-9, s] for p in self.edge]
        pt = [[p[0]*10e-9, p[1]*10e-9, s+h] for p in self.edge]

        print(pb)
        print(pt)

        p_array = [pb[0], pt[0], pt[1], pb[1]]

        points = []
        for point in p_array:
            new_point = geom.add_point(point, 0.05)
            points.append(new_point)

        points = points + [points[0]]

        lines = []
        for point1, point2 in zip(points[:-1], points[1:]):
            line = geom.add_line(point1, point2)
            lines.append(line)

        line_loop = geom.add_line_loop(lines)

        surf1 = geom.add_plane_surface(line_loop)
        geom.add_physical_surface(surf1, label=self.id)

        # return line_loop

    def set_vector(self):
        ll = 0
        for pp1, pp2 in zip(self.points[:-2], self.points[1:]):
            p1, p2 = Point(pp1), Point(pp2)

            if distance(p1, p2) > ll:
                ll = distance(p1, p2)
                self.slope = slope(p1, p2)

    def metal_connection(self, cell, datafield, name):
        for gds, metal in datafield.wires.items():
            m1 = name.split(' ')[1]
            m2 = name.split(' ')[2]

            # TODO: Solve this fucking issue with the ground M0.
            if metal.name in [m1, m2]:
                self.metals.append(gds)
        print(self.metals)

    def metal_edges(self, datafield):
        gds = self.metals[0]
        for poly in datafield.polygons[gds][0]:
            points = np.vstack([poly.points, poly.points[0]])
            for pp1, pp2 in zip(points[:-1], points[1:]):
                for path in tools.angusj_path([pp1, pp2], self.points):
                    p1, p2 = Point(path[0]), Point(path[1])
                    if self.slope == slope(p1, p2):
                        self.edge = path


class Point:
    def __init__ (self, point):
        self.x = point[0]
        self.y = point[1]


def distance(p1, p2):
    return np.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)


def slope(p1, p2, tol=1e-9):

    if abs(p1.x - p2.x) < tol:
        ss = [1, 0, 0]
    elif abs(p1.y - p2.y) < tol:
        ss = [0, 1, 0]
    else:
        ss = (p1.y - p2.y) / (p1.x - p2.x)

    if isinstance(ss, list):
        if ss[0] == 1:
            return 'x'
        elif ss[1] == 1:
            return 'y'
        else:
            raise ValueError('check slope algorithm')
    else:
        return ss
