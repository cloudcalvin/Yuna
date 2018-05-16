import numpy as np
import pyclipper
import gdspy

from yuna import utils
from yuna import grid

from yuna import lvs

from collections import namedtuple
from collections import defaultdict
import collections as cl

from shapely.geometry import Polygon as ShapePolygon


class Paths(object):

    def __init__(self, gds, pdk, poly):
        self.key = (gds, 0)
        self.datatype = 0
        self.raw_points = poly[(gds, 0)]
        self.union_points = self.union()

        # self.data = fabdata[gds]
        #
        # assert isinstance(self.data.name, str)
        #
        # if self.data is None:
        #     raise ValueError('Polygon data cannot be None.')

        self.points = self.simple()
        self.polygons = []

    def add_polygon(self, dt, element, key=None, holes=None):
        """
        Add a new element or list of elements to this cell.

        Parameters
        ----------
        element : object
            The element or list of elements to be inserted in this cell.

        Returns
        -------
        out : ``Cell``
            This cell.
        """

        if key is None:
            raise TypeError('key cannot be None')

        assert isinstance(element[0], list)

        polygon = lvs.geometry.Polygon(key, element, dt.pcd, holes)
        self.polygons.append(polygon)

    def simple(self):
        points = list()
        for pp in self.union_points:
            if len(pp) > 10:
                factor = (len(pp)/100.0) * 1e5
                sp = ShapePolygon(pp).simplify(factor)
                plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]
                points.append(plist[:-1])
            else:
                points.append(list(pp))
        return grid.snap_points(points)

    def union(self):
        if not isinstance(self.raw_points[0][0], np.ndarray):
            raise TypeError("poly must be a 3D list")

        cc_poly = list()

        for poly in self.raw_points:
            if pyclipper.Orientation(poly) is False:
                reverse_poly = pyclipper.ReversePath(poly)
                cc_poly.append(reverse_poly)
            else:
                cc_poly.append(poly)

        union = utils.angusj(subj=cc_poly, method='union')
        points = pyclipper.CleanPolygons(union)

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def create_mask(self, datafield, myCell):

        named_layers = defaultdict(dict)

        for l1 in self.points:
            Polygon = namedtuple('Polygon', ['area', 'points'])
            pp = Polygon(area=pyclipper.Area(l1), points=l1)

            if pp.area < 0:
                if 'holes' in named_layers:
                    named_layers['holes'].append(pp)
                else:
                    named_layers['holes'] = [pp]
            elif pp.area > 0:
                if 'polygon' in named_layers:
                    named_layers['polygon'].append(pp)
                else:
                    named_layers['polygon'] = [pp]
            else:
                raise ValueError('polygon area cannot be zero')

        for poly in named_layers['polygon']:
            add_to_mask = True

            for hole in named_layers['holes']:
                if abs(hole.area) < abs(poly.area):

                    if utils.is_nested_polygons(hole, poly):
                        datafield.add(poly.points, self.key, holes=hole.points, model='model')
                        myCell.add(gdspy.Polygon(hole.points, layer=81))
                        add_to_mask = False
                    else:
                        datafield.add(poly.points, self.key, model='model')
                        add_to_mask = False

            if add_to_mask:
                datafield.add(poly.points, self.key, model='model')

            myCell.add(gdspy.Polygon(poly.points, self.key[0], verbose=False))

    def add(self, mask):
        self.points = utils.angusj(self.points, mask.points, 'difference')

    def update_mask(self, datafield):
        for pp in self.points:
            self.add_polygon(datafield, pp, self.key)
