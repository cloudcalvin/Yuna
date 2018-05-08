import numpy as np
import pyclipper
import gdspy

from yuna import utils

from collections import namedtuple
from collections import defaultdict

from shapely.geometry import Polygon


class Metal(object):

    def __init__(self, gds, poly):
        self.key = (gds, 0)
        self.raw_points = poly[(gds, 0)]
        self.union_points = self.union()
        self.points = self.simple()

    def simple(self):
        points = list()
        for pp in self.union_points:
            if len(pp) > 10:
                factor = (len(pp)/100.0) * 1e5 
                sp = Polygon(pp).simplify(factor)
                plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]
                points.append(plist[:-1])
            else:
                points.append(list(pp))
        return points

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

    def add(self, element):
        self.points = utils.angusj(self.points, element.points, 'difference')

        # diff_points = utils.angusj(self.points, element.points, 'difference')

        # pp = list()
        # if isinstance(element, Via):
        #     for poly in diff_points:
        #         if pyclipper.Orientation(poly) is False:
        #             reverse_poly = pyclipper.ReversePath(poly)
        #             # cc_poly.append(reverse_poly)
        #             print('--- Negative poly')
        #             # print(poly)
        #         else:
        #             pp.append(poly)
        #             # cc_poly.append(poly)
        #             print('--- Positive poly')
        #             # print(poly)

        # print(pp)
        # self.points = pp

        # print('---\n')

    def update_mask(self, datafield):
        for pp in self.points:
            datafield.add(pp, self.key)


class Via(object):

    def __init__(self, gds, poly):
        self.clip = False
        self.key = (gds, 1)
        self.raw_points = poly[(gds, 1)]
        self.union_points = self.union()
        self.points = self.simple()

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
        return points

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield, element=None):
        if element is not None:
            self.points = utils.angusj(self.points, element.points, 'difference')

        for pp in self.points:
            datafield.add(pp, self.key)

        self.clip = True


class Junction(object):

    def __init__(self, gds, poly):
        self.key = (gds, 3)
        self.raw_points = poly[(gds, 3)]
        self.union_points = self.union()
        self.points = self.simple()

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
        return points

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield):
        for pp in self.points:
            datafield.add(pp, self.key)


class Ntron(object):

    def __init__(self, gds, poly):
        self.key = (gds, 7)
        self.raw_points = poly[(gds, 7)]
        self.union_points = self.union()
        self.points = self.simple()

    def simple(self):
        points = list()
        for pp in self.union_points:
            if len(pp) > 10:
                factor = (len(pp)/150.0) * 1e5 
                sp = Polygon(pp).simplify(factor)
                plist = [[int(p[0]), int(p[1])] for p in sp.exterior.coords]
                points.append(plist[:-1])
            else:
                points.append(list(pp))
        return points

    def union(self):
        points = utils.angusj(subj=self.raw_points, method='union')

        if not isinstance(points[0][0], list):
            raise TypeError("poly must be a 3D list")

        return points

    def update_mask(self, datafield):
        for pp in self.points:
            datafield.add(pp, self.key)
