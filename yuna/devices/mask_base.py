from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon


class MaskBase(object):

    def __init__(self, key, poly):
        self.key = key

        if self.key is None:
            raise TypeError('`key` cannot be None')

        self.raw_points = poly[key]
        self.points = self.simple()
        self.polygons = []

    def simple(self):
        points = list()
        for pp in self.union():
            if len(pp) > 10:
                factor = (len(pp)/20.0) * 1e5
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

            polygon = lvs.geometry.Polygon(self.key, pp, datafield.pcd)
            self.polygons.append(polygon)
