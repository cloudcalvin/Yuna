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
from yuna.lvs.poly_base import PolyBase

from .mask_base import MaskBase


class Path(MaskBase):

    def __init__(self, gds, poly):
        super(Path, self).__init__((gds, 0), poly, 100.0)
        self.datatype = 0
        self.polygons = []

    def __str__(self):
        pass

    # def union(self):
    #     cc_poly = list()
    #
    #     for poly in self.raw_points:
    #         if pyclipper.Orientation(poly) is False:
    #             reverse_poly = pyclipper.ReversePath(poly)
    #             cc_poly.append(reverse_poly)
    #         else:
    #             cc_poly.append(poly)
    #
    #     union = utils.angusj(subj=cc_poly, method='union')
    #     points = pyclipper.CleanPolygons(union)
    #
    #     if not isinstance(points[0][0], list):
    #         raise TypeError("poly must be a 3D list")
    #
    #     return points

    def create_mask(self, geom, myCell):

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
                        geom.add(poly.points, self.key, holes=hole.points, model='model')
                        myCell.add(gdspy.Polygon(hole.points, layer=81))
                        add_to_mask = False
                    else:
                        geom.add(poly.points, self.key, model='model')
                        add_to_mask = False

            if add_to_mask:
                geom.add(poly.points, self.key, model='model')

            myCell.add(gdspy.Polygon(poly.points, self.key[0], verbose=False))

    def diff(self, mask):
        self.points = utils.angusj(self.points, mask.points, 'difference')

    def add_polygon(self, geom):
        for pp in self.points:
            assert isinstance(pp[0], list)

            data = geom.raw_pdk_data['Layers']

            layers = [*data['ix']]

            for params in layers:
                if params['layer'] == self.key[0]:
                    params['datatype'] = self.key[1]
                    polygon = PolyBase(pp, params)
                    self.polygons.append(polygon)
