from yuna import utils
from yuna import grid

import numpy as np

from yuna.lvs.poly_base import PolyBase

from shapely.geometry import Polygon


class MaskBase(object):

    _PP = 10
    _FACTOR = 1e5

    def __init__(self, key, poly, smoothness=1.0):
        self.key = key
        self.smoothness = smoothness

        if self.key is None:
            raise TypeError('`key` cannot be None')

        self.raw_points = poly[key]

        if not isinstance(self.raw_points[0][0], np.ndarray):
            raise TypeError("raw_points must be a 3D list")

        self.points = self.simple()
        self.polygons = []

    def simple(self):
        points = list()
        for pp in self.union():
            if len(pp) > MaskBase._PP:
                factor = (len(pp)/self.smoothness) * MaskBase._FACTOR
                sp = Polygon(pp).simplify(factor)
                plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]
                points.append(plist[:-1])
            else:
                points.append(list(pp))
        return grid.snap_points(points)

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield):
        for pp in self.points:
            assert isinstance(pp[0], list)

            polygon = PolyBase(self.key, pp, datafield.pcd)
            self.polygons.append(polygon)
