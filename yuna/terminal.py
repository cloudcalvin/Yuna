import gdspy
import pygmsh
import meshio
import numpy as np
import pyclipper

from yuna import utils
from collections import namedtuple

from .utils import nm
from .utils import um


class Point:
    def __init__ (self, point):
        self.x = point[0]
        self.y = point[1]


class Terminal(object):
    _ID = 0

    def __init__(self, points):
        self.id = '.t {}'.format(Terminal._ID)
        Terminal._ID += 1

        self.points = points[0]
        self.edge = []
        self.slope = None
        self.metals = list()
        self.surface = None

    def set_slope(self):
        ll = 0
        for pp1, pp2 in zip(self.points[:-2], self.points[1:]):
            p1, p2 = Point(pp1), Point(pp2)

            if distance(p1, p2) > ll:
                ll = distance(p1, p2)
                self.slope = slope(p1, p2)

    def metal_connection(self, datafield, name):
        wires = {**datafield.pcd.layers['ix'],
                 **datafield.pcd.layers['term'],
                 **datafield.pcd.layers['res']}

        for gds, metal in wires.items():
            m1 = name.split(' ')[1]
            m2 = name.split(' ')[2]

            # TODO: Solve this fucking issue with the ground M0.
            if metal.name in [m1, m2]:
                self.metals.append(gds)

    def metal_edge(self, datafield):
        gds = self.metals[0]
        for poly in datafield.polygons[gds][0]:
            points = np.vstack([poly.points, poly.points[0]])
            for pp1, pp2 in zip(points[:-1], points[1:]):
                for path in utils.angusj_path([pp1, pp2], self.points):
                    p1, p2 = Point(path[0]), Point(path[1])
                    if self.slope == slope(p1, p2):
                        self.edge = path

    def extrude(self, geom, datafield):
        gds = self.metals[0]
        polygon = datafield.polygons[gds][0]

        s = polygon[0].data.position * um
        h = polygon[0].data.width * um

        pb = [[p[0]*nm, p[1]*nm, s] for p in self.edge]
        pt = [[p[0]*nm, p[1]*nm, s+h] for p in self.edge]

        coords = [pb[0], pt[0], pt[1], pb[1]]

        ll = line_loop(geom, coords)

        surf = geom.add_plane_surface(ll)
        self.surface = geom.add_physical_surface(surf, label=self.id)


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


def line_loop(geom, coords):
    points = []
    for point in coords:
        new_point = geom.add_point(point, 0.05)
        points.append(new_point)

    points = points + [points[0]]

    lines = []
    for point1, point2 in zip(points[:-1], points[1:]):
        line = geom.add_line(point1, point2)
        lines.append(line)

    return geom.add_line_loop(lines)
