from yuna import utils
from yuna import grid
from yuna import lvs

from shapely.geometry import Polygon


class Via(object):

    def __init__(self, gds, pdk, poly):
        self.clip = False
        self.key = (gds, 1)
        self.datatype = 1
        self.raw_points = poly[(gds, 1)]
        self.union_points = self.union()

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

    def add(self, mask):
        self.points = utils.angusj(self.points, mask.points, 'difference')
        self.clip = True

    def update_mask(self, datafield, element=None):
        for pp in self.points:
            self.add_polygon(datafield, pp, self.key)