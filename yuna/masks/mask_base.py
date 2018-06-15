from yuna import utils
from yuna import grid

import numpy as np
import pyclipper

from shapely.geometry import Polygon


class MaskBase(object):
    """
    The base class for creating polygons from the
    gds file. These polygons are merged and smoothed
    for meshing.

    Parameters
    ----------
    key : tuple
        Contains the gdsnumber and the datatype (layer, datatype).
    smoothness : float
        A constant with which to smooth the polygons.
    raw_points : array-like
        The original polygon points as read-in by the gdspy library.
    points : array-like
        The raw_points with the smoothing algorithm applied.
    polygons : list
        List of PolyBase polygons that contains the polygons
        points and the PDK data connected to that specific polygon.

    Notes
    -----
    The simplified and merging operations are applied on
    objecct creation. This can be updated to use Python's
    magix functions.
    """

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

        self.points = self.simplify()

    def simplify(self):
        points = list()
        for pp in self._union():
            if len(pp) > MaskBase._PP:
                factor = (len(pp)/self.smoothness) * MaskBase._FACTOR
                sp = Polygon(pp).simplify(factor)
                plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]
                points.append(plist[:-1])
            else:
                points.append(list(pp))
        return grid.snap_points(points)

    def _union(self):
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

    # def union(self):
    #     points = utils.angusj(subj=self.raw_points, method='union')
    #
    #     if not isinstance(points[0][0], list):
    #         raise TypeError("poly must be a 3D list")
    #
    #     return points
